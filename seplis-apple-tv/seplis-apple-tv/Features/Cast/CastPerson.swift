import Foundation

nonisolated struct CastPerson: Decodable, Identifiable {
    let id: Int
    let name: String
    let profileImage: Poster?
}

nonisolated struct CastMember: Identifiable {
    let person: CastPerson
    let roles: [String]

    var id: Int { person.id }
}
