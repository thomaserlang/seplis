import TVServices

final class ContentProvider: TVTopShelfContentProvider {
    override func loadTopShelfContent(completionHandler: @escaping ((any TVTopShelfContent)?) -> Void) {
        guard let snapshot = TopShelfStore().load(), !snapshot.items.isEmpty else {
            completionHandler(nil)
            return
        }
        let items = snapshot.items.map { entry in
            let item = TVTopShelfSectionedItem(identifier: "\(snapshot.accountID)-\(entry.identifier)")
            item.title = entry.title
            item.imageShape = .poster
            item.setImageURL(entry.imageURL, for: .screenScale1x)
            item.setImageURL(entry.imageURL, for: .screenScale2x)
            item.playbackProgress = min(1, max(0, entry.progress))
            item.playAction = TVTopShelfAction(url: TopShelfLink(accountID: snapshot.accountID, entry: entry, play: true).url)
            item.displayAction = TVTopShelfAction(url: TopShelfLink(accountID: snapshot.accountID, entry: entry, play: false).url)
            return item
        }
        let section = TVTopShelfItemCollection(items: items)
        section.title = "Continue Watching"
        completionHandler(TVTopShelfSectionedContent(sections: [section]))
    }
}
