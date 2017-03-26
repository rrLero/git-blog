import math


class Pagination:
    def __init__(self, per_page, page, count):
        self.per_page = per_page
        self.page = page
        self.count = count
        self.first_post = self.per_page * (self.page - 1)
        self.last_post = self.per_page * (self.page - 1) + self.per_page - 1
        if self.last_post >= count - 1:
            self.last_post = count - 1
        if self.first_post > 1:
            self.has_prev = True
        else:
            self.has_prev = False
        if self.page < math.ceil(self.count/self.per_page):
            self.has_next = True
        else:
            self.has_next = False
        if self.page > 1:
            self.prev_num = page - 1
        else:
            self.prev_num = False
        if self.page < math.ceil(self.count/self.per_page):
            self.next_num = self.page + 1
        else:
            self.next_num = False

    def first_post(self):
        return self.first_post

    def last_post(self):
        return self.last_post

    def has_prev(self):
        return self.has_prev

    def has_next(self):
        return self.has_next