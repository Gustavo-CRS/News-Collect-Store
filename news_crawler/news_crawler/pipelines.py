from itemadapter import ItemAdapter

class NewsCrawlerPipeline:
    def process_item(self, item, spider):
        return item