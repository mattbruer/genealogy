// Reads text lines (with pixel boxes) from images using macOS Vision.
// Usage: swift ocr.swift out.json img1 img2 ...
import Foundation
import Vision
import AppKit

struct Line: Codable { let text: String; let conf: Float; let x: Int; let y: Int; let w: Int; let h: Int }
struct Result: Codable { let file: String; let width: Int; let height: Int; let lines: [Line] }

func recognize(_ path: String) -> Result? {
    guard let image = NSImage(contentsOfFile: path),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    let w = cg.width, h = cg.height
    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    try? VNImageRequestHandler(cgImage: cg).perform([request])
    let lines = (request.results ?? []).compactMap { obs -> Line? in
        guard let top = obs.topCandidates(1).first else { return nil }
        let b = obs.boundingBox
        return Line(text: top.string, conf: top.confidence,
                    x: Int(b.minX * Double(w)), y: Int((1 - b.maxY) * Double(h)),
                    w: Int(b.width * Double(w)), h: Int(b.height * Double(h)))
    }
    return Result(file: path, width: w, height: h, lines: lines)
}

let args = CommandLine.arguments
let results = args.dropFirst(2).compactMap(recognize)
let data = try! JSONEncoder().encode(results)
try! data.write(to: URL(fileURLWithPath: args[1]))
print("ocr: \(results.count) images")
