import AppKit
import Foundation

let args = CommandLine.arguments
guard [3, 5].contains(args.count),
      let image = NSImage(contentsOfFile: args[1]) else {
    fputs("Unable to decode SVG\n", stderr)
    exit(1)
}
let scale: CGFloat = 2
let size = image.size
let width = args.count == 5 ? Int(args[3])! : Int(size.width * scale)
let height = args.count == 5 ? Int(args[4])! : Int(size.height * scale)
guard let bitmap = NSBitmapImageRep(bitmapDataPlanes: nil,
                                  pixelsWide: width,
                                  pixelsHigh: height,
                                  bitsPerSample: 8,
                                  samplesPerPixel: 4,
                                  hasAlpha: true,
                                  isPlanar: false,
                                  colorSpaceName: .deviceRGB,
                                  bytesPerRow: 0,
                                  bitsPerPixel: 0),
      let context = NSGraphicsContext(bitmapImageRep: bitmap) else { exit(2) }
NSGraphicsContext.saveGraphicsState()
NSGraphicsContext.current = context
image.draw(in: NSRect(x: 0, y: 0, width: width, height: height))
NSGraphicsContext.restoreGraphicsState()
guard let data = bitmap.representation(using: .png, properties: [:]) else { exit(3) }
try data.write(to: URL(fileURLWithPath: args[2]))
print(args[2])
