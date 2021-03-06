from libs.base_client import BaseClient
from libs.common import format_url, md5
from libs.request import Request


class VmGirls(BaseClient):

    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.vmgirls.com'
        self.start_url = f'{self.base_url}/archives.html'

    def parse(self, response):
        doc = response.doc
        data = []
        i = 0
        for element in doc('.archives a').items():
            url = element.attr('href')
            if url.find('html') == -1:
                continue
            i += 1
            if i > 10:
                break
            url = format_url(url, self.base_url)
            data.append(Request(url, self.parse_page))
        return data

    def parse_page(self, response):
        doc = response.doc

        title = doc('.post-title').text()
        image_list = []
        for item in doc('.nc-light-gallery img').items():
            image_list.append(f"https:{item.attr('src')}")

        tag_list = []
        for item in doc('.post-tags a').items():
            tag_list.append(item.text())

        self.logger.info(f"{response.index}/{response.total}: {title}.")

        return {'title': title, 'image': image_list, 'tag': tag_list, 'url': response.url}

    def save(self, data):
        db = self.get_db()
        col = db.get_collection('vmgirls')
        for item in data:
            _id = md5(item['title'])
            if not col.find_one({'_id': _id}):
                item['download'] = 0
                item['imgur_id'] = ''
            col.update_one({'_id': _id}, {'$set': item}, True)
