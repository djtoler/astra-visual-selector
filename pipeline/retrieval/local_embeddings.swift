import Foundation
import NaturalLanguage

// The system model is local. No input text is sent to an embedding service.
guard let model = NLEmbedding.wordEmbedding(for: .english) else {
    fputs("macOS English word embedding is unavailable\n", stderr)
    exit(1)
}

let input = FileHandle.standardInput.readDataToEndOfFile()
guard let request = try JSONSerialization.jsonObject(with: input) as? [String: Any],
      let texts = request["texts"] as? [String] else {
    fputs("Expected JSON object with texts array\n", stderr)
    exit(2)
}

let pattern = try NSRegularExpression(pattern: "[A-Za-z]+")
func tokens(_ text: String) -> [String] {
    let range = NSRange(text.startIndex..<text.endIndex, in: text)
    return pattern.matches(in: text, range: range).compactMap { match in
        guard let swiftRange = Range(match.range, in: text) else { return nil }
        return String(text[swiftRange]).lowercased()
    }
}

let documents = texts.map(tokens)
var documentFrequency: [String: Int] = [:]
for words in documents {
    for word in Set(words) { documentFrequency[word, default: 0] += 1 }
}
let count = Double(texts.count)
let dimension = model.dimension
var vectors: [[Double]] = []
var wordCoverage: [Double] = []
var cache: [String: [Double]?] = [:]
for words in documents {
    var sum = [Double](repeating: 0, count: dimension)
    var totalWeight = 0.0
    var covered = 0
    for word in words {
        let vector: [Double]?
        if let cached = cache[word] { vector = cached }
        else {
            vector = model.vector(for: word)
            cache[word] = vector
        }
        guard let vector else { continue }
        covered += 1
        let frequency = Double(documentFrequency[word] ?? 1)
        let weight = log((count + 1.0) / (frequency + 1.0)) + 1.0
        for index in 0..<dimension { sum[index] += vector[index] * weight }
        totalWeight += weight
    }
    if totalWeight > 0 {
        for index in 0..<dimension { sum[index] /= totalWeight }
    }
    vectors.append(sum)
    wordCoverage.append(words.isEmpty ? 0.0 : Double(covered) / Double(words.count))
}

let output: [String: Any] = [
    "model": "macOS NaturalLanguage English word embedding; IDF-weighted mean",
    "dimension": dimension,
    "vectors": vectors,
    "wordCoverage": wordCoverage,
]
let encoded = try JSONSerialization.data(withJSONObject: output)
FileHandle.standardOutput.write(encoded)
