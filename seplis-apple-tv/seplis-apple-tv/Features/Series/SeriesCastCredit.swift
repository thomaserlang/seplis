import Foundation

nonisolated struct SeriesCastCredit: Decodable {
    let person: CastPerson
    let roles: [Role]

    nonisolated struct Role: Decodable {
        let character: String?
    }

    var member: CastMember {
        CastMember(person: person, roles: roles.compactMap(\.character).filter { !$0.isEmpty })
    }
}
