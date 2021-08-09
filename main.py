import feedparser
import csv
from datetime import datetime
from genrss import GenRSS
import re
import os
import glob

def regrex(str):
    reg = re.compile(r"<[^>]*?>")
    return reg.sub("", str)

def truncate(string, length, ellipsis='...'):
    '''文字列を切り詰める

    string: 対象の文字列
    length: 切り詰め後の長さ
    ellipsis: 省略記号
    '''
    return string[:length] + (ellipsis if string[length:] else '')

class FeedController:
    def __init__(self, name):
        self.csv_dir = "csv"
        self.xml_dir = "dist"
        self.feed_list = []
        self.entries = []
        self.name = name

        print("init end")
    
    def read_csv(self):
        '''csvファイルを読み込む

        '''
        # ファイルパスの作成
        file_path = "{}/{}.csv".format(self.csv_dir, self.name)

        # csvファイルを読み込む
        with open(file_path, newline='', encoding='utf_8') as f:
            reader = csv.DictReader(f)
            self.feed_list = [row for row in reader]

        print("read_csv end")

    def get_feed(self):
        '''feed情報からentryを取得する

        feeds: csvの中に入っているフィード情報一式
       '''
        for feed in self.feed_list:
            self.entries.extend(self._get_entries(feed))
        
        print("get_feed end")

    def view_entries(self):
        for entry in self.entries:
            print(entry)

    def _get_entries(self, feed):
        '''エントリーを取得する
        
        feed: フィード情報（Media名とrssのURL）
        '''
        posts = []
        posts.extend(feedparser.parse(feed['url']).entries)

        entries = []
        for post in posts:
            item = {}

            # タイトル取得
            # Media名を先頭につけたものを格納する。
            title = "[{}] {}".format(feed['media'], post.title)
            item['title'] = title
            
            item['link'] = post.link
            item['updated'] = post.updated

            # サマリー取得
            # なかった場合はブランクを指定
            # if 'summary' not in post.keys():
            #     summary = ""
            # else:
            #     summary = truncate(post.summary, 50)
            if post.get('summary') != None:
                summary = regrex(post.summary)
                item['summary'] = truncate(summary, 100)
            else:
                item['summary'] = ""

            # 投稿日時取得
            if post.get('published') != None:
                item['published'] = post.published
            else:
                item['published'] = datetime.utcnow()

            # 更新日時取得
            if post.get('updated') != None:
                item['updated'] = post.updated
            else:
                item['updated'] = item['published']

            entries.append(item)
        
        return entries

    def generate_xml(self):
        '''フィード作成
        
        '''
        feed = GenRSS(
            title = 'yatta47 feed({})'.format(self.name),
            site_url = 'https://yatta47.github.io',
            feed_url = 'https://yatta47.github.io'
        )

        for post in self.entries:
            feed.item(
                title = post['title'],
                description = post['summary'],
                url = post['link'],
                # author = post.author,
                pub_date = post['published']
            )

        xml = feed.xml()

        path_w = "{}/{}.xml".format(self.xml_dir, self.name)

        with open(path_w, mode='w') as f:
            f.write(xml)

        print("generate_xml end")

    def view_feed_list(self):
        for feed in self.feed_list:
            print(feed)

    def get_category_name(self, file_path):
        self.name = os.path.splitext(os.path.basename(file_path))[0]


# --------------------------------------------------------------------
# Main
# --------------------------------------------------------------------

if __name__ == "__main__":
    # kafka = FeedController("kafka")
    # kafka.read_csv()
    # kafka.get_feed()
    # kafka.generate_xml()

    files = glob.glob("csv/*.csv")
    for file in files:
        # print(file)
        print(os.path.splitext(os.path.basename(file))[0])
        category = os.path.splitext(os.path.basename(file))[0]

        f = FeedController(category)
        f.read_csv()
        f.get_feed()
        f.generate_xml()