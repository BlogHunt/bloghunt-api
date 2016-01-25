from urllib import parse


class FeedPage(object):

    def __init__(self, tree, url='', defaultns=''):
        self.tree = tree
        self.defaultns = defaultns
        self.url = url

    @property
    def title(self):
        title_elem = self.tree.find('{}title'.format(self.defaultns))
        return title_elem.text if title_elem is not None else None

    @property
    def description(self):
        description_elem = self.tree.find('{}description'.format(self.defaultns))
        return description_elem.text if description_elem is not None else None

    @property
    def link(self):
        link_elems = self.tree.findall('{}link'.format(self.defaultns))
        for link_elem in link_elems:
            if link_elem.attrib.get('rel') == 'self':
                continue
            link = link_elem.text or link_elem.attrib.get('href')
            if self.url and link:
                link = parse.urljoin(self.url, link)
            return link

    @property
    def categories(self):
        return [e.text for e in self.tree.findall('{}category'.format(self.defaultns)) if e and e.text]

    @property
    def image(self):
        image_elems = self.tree.findall('{}image/url'.format(self.defaultns))
        for image_elem in image_elems:
            if image_elem.attrib.get('rel') == 'self':
                continue
            image = image_elem.text or image_elem.attrib.get('href')
            return image

    @property
    def cloud(self):
        cloud_elems = self.tree.findall('{}cloud'.format(self.defaultns))
        for cloud_elem in cloud_elems:
            if cloud_elem.attrib.get('rel') == 'self':
                continue
            cloud = cloud_elem.text or cloud_elem.attrib.get('href')
            return cloud
