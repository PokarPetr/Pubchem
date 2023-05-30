import sqlite3, json, copy

class GroupElementsPipeline:
    def __init__(self):
        self.elems = dict()

    def process_item(self, item, spider):
        cg = item['chemical_group']

        if cg not in self.elems:
            self.elems[cg] = dict(elements_count=0, elements=list())

        item_copy = copy.deepcopy(item)
        del item_copy['chemical_group']
        self.elems[cg]['elements'].append(dict(item))
        self.elems[cg]['elements_count'] += 1
        return item

    def close_spider(self, spider):
        with open('grouped_elements.json', 'w') as f:
            json.dump(self.elems, f)


class ElemsPipeline:
    def __init__(self):
        self.conn = sqlite3.connect('elements.db')
        self.cursor = self.conn.cursor()

    def open_spider(self, spider):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS periodic_elements (
        symbol TEXT PRIMARY KEY,
        name TEXT,
        atomic_number INTEGER,
        atomic_mass REAL,
        chemical_group TEXT)
        """)
        self.conn.commit()

    def process_item(self, item, spider):
        self.cursor.execute("INSERT OR IGNORE INTO periodic_elements VALUES (?, ?, ?, ?, ?)",(
                         item['symbol'],
                         item['name'],
                         item['atomic_number'],
                         item['atomic_mass'],
                         item['chemical_group'],
                         ))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.conn.close()

