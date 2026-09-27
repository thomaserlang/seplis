import Foundation

nonisolated extension PlaySource {
    private enum CodingKeys: String, CodingKey {
        case index, duration, bitrate, codec, resolution, audio, subtitles
        case width, height, format, fps, size, videoColorRange, videoColorRangeType, mediaType
    }

    init(from decoder: any Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        index = try values.decode(Int.self, forKey: .index)
        duration = try values.decodeServerDecimal(forKey: .duration)
        bitrate = try values.decode(Double.self, forKey: .bitrate)
        codec = try values.decode(String.self, forKey: .codec)
        resolution = try values.decode(String.self, forKey: .resolution)
        audio = try values.decodeIfPresent([PlayStream].self, forKey: .audio) ?? []
        subtitles = try values.decodeIfPresent([PlayStream].self, forKey: .subtitles) ?? []
        width = try values.decodeIfPresent(Int.self, forKey: .width)
        height = try values.decodeIfPresent(Int.self, forKey: .height)
        format = try values.decodeIfPresent(String.self, forKey: .format)
        fps = values.contains(.fps) ? try values.decodeServerDecimal(forKey: .fps) : 0
        size = try values.decodeIfPresent(Int.self, forKey: .size)
        videoColorRange = try values.decodeIfPresent(String.self, forKey: .videoColorRange)
        videoColorRangeType = try values.decodeIfPresent(String.self, forKey: .videoColorRangeType)
        mediaType = try values.decodeIfPresent(String.self, forKey: .mediaType)
    }
}

nonisolated extension PlayStream {
    private enum CodingKeys: String, CodingKey {
        case title, language, groupIndex, forced, codec, channels
    }

    init(from decoder: any Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        title = try values.decodeIfPresent(String.self, forKey: .title)
        language = try values.decode(String.self, forKey: .language)
        groupIndex = try values.decodeIfPresent(Int.self, forKey: .groupIndex)
        forced = try values.decodeIfPresent(Bool.self, forKey: .forced) ?? false
        codec = try values.decodeIfPresent(String.self, forKey: .codec)
        channels = try values.decodeIfPresent(Int.self, forKey: .channels)
    }
}

nonisolated private extension KeyedDecodingContainer {
    // Pydantic serializes Decimal as a JSON string; also accept the older numeric encoding.
    func decodeServerDecimal(forKey key: Key) throws -> Double {
        let number: Double?
        if let value = try? decode(Double.self, forKey: key) {
            number = value
        } else {
            number = Double(try decode(String.self, forKey: key))
        }
        guard let number, number.isFinite, number >= 0 else {
            throw DecodingError.dataCorruptedError(forKey: key, in: self,
                                                   debugDescription: "Expected a nonnegative decimal value.")
        }
        return number
    }
}
