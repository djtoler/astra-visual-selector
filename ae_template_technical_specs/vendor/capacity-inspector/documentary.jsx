// ES3-compatible ExtendScript. Run through run.py, which supplies the job object.
(function () {
    var job = /*JOB*/;
    if (job.mode !== "inspect" && (!job.selection_gate || job.selection_gate.policyVersion !== "six-options-v2"))
        throw Error("RENDER BLOCKED: use run.py with a validated six-choice selection review.");
    function encode(v) {
        if (v === null) return 'null';
        if (typeof v === 'undefined') return 'null';
        if (typeof v === 'string') return '"' + v.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/[\x00-\x1f]/g, function(c) { return '\\u' + ('0000' + c.charCodeAt(0).toString(16)).slice(-4); }) + '"';
        if (typeof v === 'number' || typeof v === 'boolean') return String(v);
        var a = [], k;
        if (v instanceof Array) { for (k = 0; k < v.length; k++) a.push(encode(v[k])); return '[' + a.join(',') + ']'; }
        for (k in v) if (v.hasOwnProperty(k)) a.push(encode(k) + ':' + encode(v[k]));
        return '{' + a.join(',') + '}';
    }
    var report = {ok:false, mode:job.mode, warnings:[], replacements:[]}, suppressed = false, openedInspectionPath = null;
    function finish() {
        var result = encode(report);
        var file = new File(job.report_file);
        file.encoding = 'UTF-8';
        if (!file.open('w')) throw Error('Cannot write the pilot report: ' + file.error);
        file.write(result); file.close();
        return result;
    }
    function itemPath(x) {
        var parts = [x.name];
        while (x.parentFolder && x.parentFolder !== app.project.rootFolder) { x = x.parentFolder; parts.unshift(x.name); }
        return parts.join('/');
    }
    function comp(name) {
        var found = null;
        for (var i = 1; i <= app.project.numItems; i++) {
            var x = app.project.item(i);
            if (x instanceof CompItem && (name.indexOf('/') >= 0 ? itemPath(x) === name : x.name === name)) {
                if (found) throw Error('Ambiguous composition: ' + name);
                found = x;
            }
        }
        if (!found) throw Error('Composition not found: ' + name);
        return found;
    }
    function objectType(x) {
        if (x instanceof CompItem) return 'CompItem';
        if (x instanceof FootageItem) return 'FootageItem';
        if (x instanceof FolderItem) return 'FolderItem';
        if (typeof TextLayer !== 'undefined' && x instanceof TextLayer) return 'TextLayer';
        if (typeof ShapeLayer !== 'undefined' && x instanceof ShapeLayer) return 'ShapeLayer';
        if (typeof CameraLayer !== 'undefined' && x instanceof CameraLayer) return 'CameraLayer';
        if (typeof LightLayer !== 'undefined' && x instanceof LightLayer) return 'LightLayer';
        if (typeof AVLayer !== 'undefined' && x instanceof AVLayer) return 'AVLayer';
        return 'Layer';
    }
    function footageSourceType(item) {
        if (!(item instanceof FootageItem)) return null;
        if (item.mainSource instanceof FileSource) return 'FileSource';
        if (item.mainSource instanceof SolidSource) return 'SolidSource';
        if (item.mainSource instanceof PlaceholderSource) return 'PlaceholderSource';
        return 'FootageSource';
    }
    function safeValue(x, name) {
        try { return x[name]; } catch (e) { return null; }
    }
    function propertyState(p, includeExpression) {
        if (!p) return null;
        var state = {numKeys:p.numKeys || 0};
        try { state.expressionEnabled = !!p.expressionEnabled; } catch (e) { state.expressionEnabled = false; }
        if (state.expressionEnabled && includeExpression) {
            try {
                state.expression = String(p.expression);
                if (state.expression.length > 20000) {
                    state.expression = state.expression.substring(0, 20000);
                    state.expressionTruncated = true;
                }
            } catch (e2) { state.expressionReadError = String(e2); }
        }
        return state;
    }
    function keyframedPropertyState(p, includeExpression) {
        var state = propertyState(p, includeExpression), keys = [];
        if (!p || !state) return state;
        for (var ki=1;ki<=state.numKeys;ki++) {
            var key = {index:ki, time:p.keyTime(ki), value:p.keyValue(ki)};
            try { key.inInterpolationType = String(p.keyInInterpolationType(ki)); } catch (inError) {}
            try { key.outInterpolationType = String(p.keyOutInterpolationType(ki)); } catch (outError) {}
            keys.push(key);
        }
        if (keys.length) state.keyframes = keys;
        return state;
    }
    function transformStates(layer) {
        var group = layer.property('ADBE Transform Group'), rows = {}, names = [
            ['anchorPoint','ADBE Anchor Point'], ['position','ADBE Position'],
            ['scale','ADBE Scale'], ['rotation','ADBE Rotate Z'], ['opacity','ADBE Opacity']
        ];
        if (!group) return rows;
        for (var i=0;i<names.length;i++) {
            var p = group.property(names[i][1]);
            if (p) rows[names[i][0]] = names[i][0] === 'opacity' ? keyframedPropertyState(p, true) : propertyState(p, true);
        }
        return rows;
    }
    function textDocumentState(td) {
        var row = {
            text:String(td.text), font:String(td.font),
            fontSize:safeValue(td,'fontSize'), leading:safeValue(td,'leading'),
            tracking:safeValue(td,'tracking'), justification:String(safeValue(td,'justification')),
            boxText:!!safeValue(td,'boxText'), boxTextSize:safeValue(td,'boxTextSize'),
            boxTextPos:safeValue(td,'boxTextPos'), allCaps:!!safeValue(td,'allCaps'),
            smallCaps:!!safeValue(td,'smallCaps'), fillColor:safeValue(td,'fillColor'),
            strokeColor:safeValue(td,'strokeColor'), strokeWidth:safeValue(td,'strokeWidth')
        };
        row.textKind = row.boxText ? 'paragraph' : 'point';
        return row;
    }
    function matchingPreviousDisposableState() {
        var states = job.allowed_previous_disposable_states || [], si, ii;
        if (!app.project || app.project.renderQueue.rendering) return null;
        var currentPath = app.project.file ? app.project.file.fsName : null;
        for (si = 0; si < states.length; si++) {
            var state = states[si], expected = state.items || [];
            if (currentPath && currentPath !== state.sourceProject) continue;
            if (app.project.numItems !== expected.length) continue;
            var matches = true;
            for (ii = 1; ii <= app.project.numItems; ii++) {
                var item = app.project.item(ii), prior = expected[ii - 1];
                if (!prior || item.id !== prior.id || item.name !== prior.name) { matches = false; break; }
            }
            if (matches) return state;
        }
        return null;
    }
    function inventory() {
        var rows = [], items = [], missing = [], usedMissingFonts = [];
        for (var i = 1; i <= app.project.numItems; i++) {
            var item = app.project.item(i);
            var itemRow = {id:item.id, name:item.name, path:itemPath(item), itemType:objectType(item)};
            if (item instanceof CompItem || item instanceof FootageItem) {
                itemRow.width = safeValue(item,'width'); itemRow.height = safeValue(item,'height');
                itemRow.pixelAspect = safeValue(item,'pixelAspect'); itemRow.duration = safeValue(item,'duration');
                itemRow.frameRate = safeValue(item,'frameRate'); itemRow.hasVideo = safeValue(item,'hasVideo');
                itemRow.hasAudio = safeValue(item,'hasAudio');
            }
            if (item instanceof FootageItem) {
                itemRow.sourceType = footageSourceType(item);
                itemRow.missing = !!item.footageMissing;
                itemRow.isStill = safeValue(item.mainSource,'isStill');
                try { itemRow.file = item.file ? item.file.fsName : null; } catch (fileError) { itemRow.file = null; }
            }
            items.push(itemRow);
            if (item instanceof FootageItem && item.footageMissing) missing.push(item.name);
            if (!(item instanceof CompItem)) continue;
            var layers = [];
            for (var j = 1; j <= item.numLayers; j++) {
                var l = item.layer(j), row = {
                    index:j, name:l.name, layerType:objectType(l),
                    inPoint:l.inPoint, outPoint:l.outPoint, startTime:l.startTime,
                    stretch:safeValue(l,'stretch'), enabled:l.enabled,
                    solo:safeValue(l,'solo'), shy:safeValue(l,'shy'), locked:safeValue(l,'locked'),
                    guideLayer:safeValue(l,'guideLayer'), adjustmentLayer:safeValue(l,'adjustmentLayer'),
                    threeDLayer:safeValue(l,'threeDLayer'), nullLayer:safeValue(l,'nullLayer'),
                    hasVideo:safeValue(l,'hasVideo'), hasAudio:safeValue(l,'hasAudio'),
                    audioEnabled:safeValue(l,'audioEnabled'), timeRemapEnabled:safeValue(l,'timeRemapEnabled'),
                    transform:transformStates(l)
                };
                if (row.timeRemapEnabled) row.timeRemap = keyframedPropertyState(l.property('ADBE Time Remapping'), true);
                if (l instanceof TextLayer) {
                    var sourceText = l.property('ADBE Text Properties').property('ADBE Text Document');
                    var td = sourceText.value;
                    row.textField = textDocumentState(td);
                    row.sourceText = propertyState(sourceText, true);
                    if (l.enabled && !l.guideLayer && td.fontObject && td.fontObject.isSubstitute) {
                        var seenFont = false;
                        for (var uf=0;uf<usedMissingFonts.length;uf++) if (usedMissingFonts[uf]===td.font) seenFont=true;
                        if (!seenFont) usedMissingFonts.push(td.font);
                    }
                }
                if (l.source) {
                    row.source = l.source.name; row.sourceId = l.source.id;
                    row.sourcePath = itemPath(l.source); row.sourceItemType = objectType(l.source);
                    row.sourceType = footageSourceType(l.source);
                    row.sourceWidth = safeValue(l.source,'width'); row.sourceHeight = safeValue(l.source,'height');
                    row.sourceDuration = safeValue(l.source,'duration'); row.sourceFrameRate = safeValue(l.source,'frameRate');
                    if (l.source instanceof FootageItem) {
                        row.sourceMissing = !!l.source.footageMissing;
                        row.sourceIsStill = safeValue(l.source.mainSource,'isStill');
                        try { row.sourceFile = l.source.file ? l.source.file.fsName : null; } catch (sourceFileError) { row.sourceFile = null; }
                    }
                }
                var effects = l.property('ADBE Effect Parade');
                if (effects && effects.numProperties) {
                    row.effects = [];
                    for (var ei = 1; ei <= effects.numProperties; ei++) {
                        var effect = effects.property(ei), effectRow = {name:effect.name,matchName:effect.matchName,index:ei};
                        try { effectRow.enabled = !!effect.enabled; } catch (effectError) {}
                        effectRow.propertyCount = effect.numProperties || 0;
                        row.effects.push(effectRow);
                    }
                }
                layers.push(row);
            }
            var controllers = [];
            try {
                for (var ci=1;ci<=item.motionGraphicsTemplateControllerCount;ci++) controllers.push({index:ci,name:item.getMotionGraphicsTemplateControllerName(ci)});
            } catch (controllerError) {}
            rows.push({name:item.name, path:itemPath(item), id:item.id, itemType:'CompItem', workAreaStart:item.workAreaStart, workAreaDuration:item.workAreaDuration, width:item.width, height:item.height, pixelAspect:item.pixelAspect, duration:item.duration, fps:item.frameRate, frameDuration:item.frameDuration, motionGraphicsControllers:controllers, layers:layers});
        }
        report.items = items;
        report.compositions = rows;
        report.missingFootage = missing;
        report.usedMissingFonts = usedMissingFonts;
        report.missingFonts = [];
        var fonts = app.fonts.missingOrSubstitutedFonts;
        for (var fi=0;fi<fonts.length;fi++) report.missingFonts.push(fonts[fi].postScriptName);
    }
    try {
        // Do not discard meaningful open work or interrupt a render. AE creates
        // a new, dirty, untitled project after closing a project; zero items and
        // an empty render queue are safe to replace between disposable jobs.
        var requestedProjectAlreadyOpen = app.project && app.project.file && app.project.file.fsName === (job.prepared_project || job.template);
        var meaningfulOpenProject = app.project && (app.project.file || app.project.numItems > 0 || app.project.renderQueue.numItems > 0);
        var priorDisposableState = app.project && app.project.dirty && meaningfulOpenProject ? matchingPreviousDisposableState() : null;
        if (app.project && (app.project.renderQueue.rendering || (app.project.dirty && meaningfulOpenProject && !priorDisposableState && !requestedProjectAlreadyOpen))) throw Error('Save the current project and finish any active render before running the pilot.');
        if (priorDisposableState) report.replacedPreviouslyInspectedDisposableState = priorDisposableState.report;
        app.beginSuppressDialogs();
        suppressed = true;
        report.phase = 'opening_project';
        if (!requestedProjectAlreadyOpen && !app.open(new File(job.prepared_project || job.template))) throw Error('After Effects did not open the project.');
        try { openedInspectionPath = app.project.file ? app.project.file.fsName : null; } catch (openedPathError) {}
        report.phase = 'inventory';
        report.aeVersion = app.version;
        function gpuLabel(type) {
            if (type === GpuAccelType.METAL) return 'Metal';
            if (type === GpuAccelType.CUDA) return 'CUDA';
            if (type === GpuAccelType.OPENCL) return 'OpenCL';
            if (type === GpuAccelType.SOFTWARE) return 'Software Only';
            return String(type);
        }
        report.gpuAcceleration = gpuLabel(app.project.gpuAccelType);
        report.availableGPUAcceleration = [];
        for (var gi = 0; gi < app.availableGPUAccelTypes.length; gi++) report.availableGPUAcceleration.push(gpuLabel(app.availableGPUAccelTypes[gi]));
        inventory();
        if (job.mode === 'inspect') {
            if (job.inspection_save) {
                var inspectionCopy = new File(job.inspection_save);
                if (inspectionCopy.exists) throw Error('Inspection backup already exists');
                app.project.save(inspectionCopy);
                report.inspectionProject = inspectionCopy.fsName;
            }
            report.sourceProject = job.template;
            report.sourceSha256 = job.source_sha256 || null;
            report.phase = 'complete';
            report.ok = true;
            report.disposableCloseRequested = !!job.disposable_staged_copy;
            // Persist the result before closing. AE can stop executing the
            // current DoScript immediately when a project closes.
            if (suppressed) { app.endSuppressDialogs(false); suppressed = false; }
            var inspectionResult = finish();
            if (job.disposable_staged_copy && openedInspectionPath) {
                var completedInspectionPath = app.project && app.project.file ? app.project.file.fsName : null;
                if (completedInspectionPath === openedInspectionPath && !app.project.renderQueue.rendering)
                    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
            }
            openedInspectionPath = null;
            return inspectionResult;
        }
        if (job.gpu_acceleration === 'Metal') {
            var supportsMetal = false;
            for (var g = 0; g < app.availableGPUAccelTypes.length; g++) if (app.availableGPUAccelTypes[g] === GpuAccelType.METAL) supportsMetal = true;
            if (!supportsMetal) throw Error('Metal GPU acceleration is unavailable.');
            report.previousGPUAcceleration = report.gpuAcceleration;
            app.project.gpuAccelType = GpuAccelType.METAL;
            report.gpuAcceleration = gpuLabel(app.project.gpuAccelType);
        }
        var i, item, name;
        for (i = 1; i <= app.project.numItems; i++) {
            item = app.project.item(i);
            if (!(item instanceof FootageItem) || !item.footageMissing) continue;
            name = item.file ? File.decode(item.file.name) : item.name;
            var relinkPath = job.relink[name] || job.relink[item.name];
            if (relinkPath) {
                var oldDuration = item.duration;
                item.replace(new File(relinkPath));
                if (!item.mainSource.isStill && item.duration < oldDuration && item.duration > 0) item.mainSource.loop = Math.min(9999,Math.ceil(oldDuration / item.duration));
            }
        }
        var key, c, l, p, doc;
        if (job.font_aliases) {
            for (i=1;i<=app.project.numItems;i++) {
                item=app.project.item(i);
                if (!(item instanceof CompItem)) continue;
                for (var li=1;li<=item.numLayers;li++) {
                    l=item.layer(li);
                    if (!(l instanceof TextLayer)) continue;
                    p=l.property('ADBE Text Properties').property('ADBE Text Document');
                    // Change only the font in each original TextDocument. Keep
                    // source-text keys, their times, and expressions intact.
                    var fontSteps = p.numKeys || 1;
                    for (var fk=1;fk<=fontSteps;fk++) {
                        doc = p.numKeys ? p.keyValue(fk) : p.valueAtTime(0, true);
                        var originalFont = doc.font;
                        if (job.font_aliases[originalFont]) {
                            try {
                                doc.font=job.font_aliases[originalFont];
                                if (p.numKeys) p.setValueAtKey(fk,doc); else p.setValue(doc);
                                report.warnings.push('Font substituted: '+originalFont+' -> '+doc.font+' in '+itemPath(item)+' / '+l.name+'. Check wrapping and readability.');
                            } catch(fontError) {
                                if (job.font_policy !== 'substitute_and_flag') throw fontError;
                                report.warnings.push('Explicit font substitution unavailable in '+itemPath(item)+' / '+l.name+': '+fontError+'. AE fallback requires visual review.');
                            }
                        }
                    }
                }
            }
        }
        for (key in job.texts) if (job.texts.hasOwnProperty(key)) {
            c = comp(key); l = null;
            for (i = 1; i <= c.numLayers; i++) if (c.layer(i) instanceof TextLayer) {
                if (l) throw Error('Multiple text layers in ' + key);
                l = c.layer(i);
            }
            if (!l) throw Error('No text layer in ' + key);
            p = l.property('ADBE Text Properties').property('ADBE Text Document');
            if (p.numKeys || p.expressionEnabled) throw Error('Animated source text requires explicit mapping: ' + key);
            doc = p.value; doc.text = job.texts[key]; p.setValue(doc);
            report.replacements.push(key);
        }
        // Explicit native text/layer inputs: no new graphics, layout, or animation.
        var nativeInputs = job.native_text_inputs || [];
        for (var ni=0;ni<nativeInputs.length;ni++) {
            var input=nativeInputs[ni]; c=comp(input.comp);l=c.layer(input.layer);
            if (!(l instanceof TextLayer) || l.name !== input.expected_name) throw Error('Native text input changed: '+input.comp);
            p=l.property('ADBE Text Properties').property('ADBE Text Document');
            if (p.numKeys) throw Error('Keyed native text needs a reviewed content mapping');
            if (p.expressionEnabled && (!input.expected_expression || p.expression !== input.expected_expression)) throw Error('Native text expression differs from inspected source');
            doc=p.valueAtTime(0,true);doc.text=input.text;p.setValue(doc);
            report.replacements.push({nativeText:input.comp,layer:input.layer,text:input.text});
        }
        var visibility=job.native_visibility || [];
        for(var vi=0;vi<visibility.length;vi++) {
            var v=visibility[vi];c=comp(v.comp);l=c.layer(v.layer);
            if(l.name!==v.expected_name || typeof v.enabled!=='boolean')throw Error('Native visibility input changed');
            l.enabled=v.enabled;
            report.replacements.push({nativeVisibility:v.comp,layer:v.layer,enabled:v.enabled});
        }
        if(job.selection_gate && job.selection_gate.renderKind==='native_template_test') {
            report.outputClassification='NATIVE_TEMPLATE_TEST_NOT_FINAL';
            report.warnings.push('Native template fit test only. Four final choices and custom-build approval gates remain enforced.');
        }
        function place(c, source, mapping) {
            mapping = mapping || {};
            // Wrap the new asset to retain the placeholder's dimensions and animation.
            if (c.numLayers > 1 && !mapping.layer) throw Error('Unexpected image slot structure: ' + c.name);
            var target = c.numLayers ? c.layer(mapping.layer || 1) : null, old = target ? target.source : null;
            if (mapping.expected_name && (!target || target.name !== mapping.expected_name)) throw Error('Image layer changed: ' + itemPath(c));
            var textPlaceholder = target instanceof TextLayer;
            if (target && !old && !textPlaceholder) throw Error('Unsupported image placeholder: ' + c.name);
            if (!source.mainSource.isStill && source.duration < c.duration) throw Error('Video is shorter than slot ' + c.name + '; supply a longer clip or still image.');
            var wrapper = app.project.items.addComp('AUTO ' + c.name, old && mapping.method !== 'add_below' ? old.width : c.width, old && mapping.method !== 'add_below' ? old.height : c.height, old && mapping.method !== 'add_below' ? old.pixelAspect : c.pixelAspect, c.duration, c.frameRate);
            var media = wrapper.layers.add(source);
            var factor = (c.name === 'LOGO' || job.image_fit === 'contain' ? Math.min : Math.max)(wrapper.width / source.width, wrapper.height / source.height) * 100;
            media.property('ADBE Transform Group').property('ADBE Scale').setValue([factor, factor]);
            media.property('ADBE Transform Group').property('ADBE Position').setValue([wrapper.width / 2, wrapper.height / 2]);
            if (mapping.method === 'add_below') {
                c.layers.add(wrapper).moveAfter(target);
            } else if (!target || textPlaceholder) {
                if (target) target.enabled = false;
                c.layers.add(wrapper);
            } else target.replaceSource(wrapper, false);
            report.replacements.push(itemPath(c));
        }
        for (key in job.images) if (job.images.hasOwnProperty(key)) {
            item = app.project.importFile(new ImportOptions(new File(job.images[key])));
            place(comp(key), item, job.image_slots ? job.image_slots[key] : null);
        }
        if (job.demo) {
            report.warnings.push('DEMO: synthetic placeholders and sample text; no user media supplied.');
            for (i = 1; i <= 8; i++) {
                name = 'IMAGE BG ' + ('0' + i).slice(-2);
                if (job.images[name]) continue;
                c = comp(name);
                var placeholder = c.layer(1).source || c;
                var demoComp = app.project.items.addComp('SAMPLE ' + i, placeholder.width, placeholder.height, placeholder.pixelAspect, c.duration, c.frameRate);
                demoComp.layers.addSolid([0.04 + i * 0.015,0.10,0.15], 'Sample background', demoComp.width, demoComp.height, demoComp.pixelAspect, demoComp.duration);
                var label = demoComp.layers.addText('SAMPLE MEDIA ' + ('0' + i).slice(-2));
                p = label.property('ADBE Text Properties').property('ADBE Text Document');
                doc = p.value; doc.fontSize = 90; doc.fillColor = [0.8,0.85,0.9]; doc.justification = ParagraphJustification.CENTER_JUSTIFY; p.setValue(doc);
                label.property('ADBE Transform Group').property('ADBE Position').setValue([demoComp.width / 2,demoComp.height / 2]);
                if (c.layer(1) instanceof TextLayer) {
                    c.layer(1).enabled = false;
                    c.layers.add(demoComp);
                } else c.layer(1).replaceSource(demoComp, false);
            }
        }
        inventory();
        if (report.missingFootage.length) throw Error('Unresolved footage: ' + report.missingFootage.join(', '));
        c = comp(job.main_comp || 'Documentary Trailer');
        if (job.bits_per_channel) {
            report.originalBitsPerChannel = app.project.bitsPerChannel;
            app.project.bitsPerChannel = job.bits_per_channel;
        }
        if (job.output_width && job.output_height) {
            var main = c;
            c = app.project.items.addComp('AUTO REVIEW ' + main.name, job.output_width, job.output_height, 1, main.duration, main.frameRate);
            var mainLayer = c.layers.add(main);
            var outputScale = Math.min(c.width/main.width,c.height/main.height)*100;
            mainLayer.property('ADBE Transform Group').property('ADBE Scale').setValue([outputScale,outputScale]);
            mainLayer.property('ADBE Transform Group').property('ADBE Position').setValue([c.width/2,c.height/2]);
            c.workAreaStart=main.workAreaStart;c.workAreaDuration=main.workAreaDuration;
        }
        // The render queue belongs to the opened template copy.
        while (app.project.renderQueue.numItems) app.project.renderQueue.item(1).remove();
        var queue = app.project.renderQueue.items.add(c);
        queue.timeSpanStart = job.render_start_seconds !== undefined ? job.render_start_seconds : (job.render_range === 'work_area' ? c.workAreaStart : 0);
        var fullDuration = job.render_range === 'work_area' ? c.workAreaDuration : c.duration;
        var remainingDuration = fullDuration - queue.timeSpanStart;
        if (remainingDuration <= 0) throw Error('Render start is outside the selected composition range.');
        queue.timeSpanDuration = job.render_duration_seconds !== undefined ? Math.min(job.render_duration_seconds, remainingDuration) : (job.preview_seconds ? Math.min(job.preview_seconds, remainingDuration) : remainingDuration);
        report.renderStartSeconds = queue.timeSpanStart;
        report.fullRenderDuration = fullDuration;
        report.mainComposition = itemPath(c);
        if (job.render_resolution) queue.setSetting('Resolution', job.render_resolution);
        report.renderSettings = queue.getSettings(GetSettingsFormat.STRING);
        var output = queue.outputModule(1);
        report.outputTemplates = output.templates;
        var requested = job.output_module || 'Lossless', exists = false;
        for (i = 0; i < output.templates.length; i++) if (output.templates[i] === requested) exists = true;
        if (!exists) throw Error('Output module unavailable: ' + requested + '. Available: ' + output.templates.join(', '));
        output.applyTemplate(requested);
        output.file = new File(job.output_dir + (requested.indexOf('H.264') === 0 ? '/video.mp4' : '/video.mov'));
        var destination = new File(job.output_dir + '/customized.aep');
        if (destination.exists || output.file.exists) throw Error('Output already exists; choose a fresh output directory.');
        app.project.save(destination);
        report.project = destination.fsName;
        report.video = output.file.fsName;
        if (job.mode === 'render') {
            if (report.usedMissingFonts.length) {
                if (job.font_policy !== 'substitute_and_flag') throw Error('Missing fonts used by visible text: ' + report.usedMissingFonts.join(', '));
                report.warnings.push('PROTOTYPE FONT FALLBACK: '+report.usedMissingFonts.join(', ')+'. Continuing with AE substitution as authorized; visual font fidelity is not verified.');
                report.fontReviewRequired = true;
            }
            if (job.max_cpu_percent) {
                app.setMultiFrameRenderingConfig(true, job.max_cpu_percent);
                report.maxCPUPercentForThisRender = job.max_cpu_percent;
            }
            report.status = 'rendering';
            finish();
            var renderStarted = new Date().getTime();
            app.project.renderQueue.render();
            if (queue.status !== RQItemStatus.DONE || !output.file.exists || output.file.length === 0) throw Error('Render did not finish successfully.');
            report.renderSeconds = (new Date().getTime() - renderStarted) / 1000;
            report.renderedDuration = queue.timeSpanDuration;
            report.rendered = true;
            report.status = 'complete';
            app.project.save(destination);
        } else report.rendered = false;
        report.ok = true;
    } catch (error) {
        report.error = String(error);
    } finally {
        if (suppressed) { app.endSuppressDialogs(false); suppressed = false; }
    }
    // Persist failures before attempting to close the disposable copy for the
    // same reason as the successful inspection path above.
    var failedResult = finish();
    if (job.mode === 'inspect' && job.disposable_staged_copy && openedInspectionPath) {
            try {
                var currentInspectionPath = app.project && app.project.file ? app.project.file.fsName : null;
                if (currentInspectionPath === openedInspectionPath && !app.project.renderQueue.rendering) {
                    app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
                    report.closedDisposableCopyAfterFailure = true;
                    openedInspectionPath = null;
                }
            } catch (cleanupError) {
                // The already-written failure report remains authoritative.
            }
    }
    return failedResult;
}());
