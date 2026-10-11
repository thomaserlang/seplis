import Foundation

nonisolated struct MovieCastCredit: Decodable {
    let person: CastPerson
    let character: String?

    var member: CastMember {
        CastMember(person: person, roles: character.map { [$0] } ?? [])
    }
}
