import math

def get_pagination(row_count=0, current_page_no=1, default_page_size=10):
    

    current_page_no = current_page_no if current_page_no >= 1 else 1

    total_pages = math.ceil(row_count / default_page_size) if row_count else 0

    if current_page_no > total_pages and total_pages != 0:
        current_page_no = total_pages

    limit = current_page_no * default_page_size
    offset = limit - default_page_size

    if limit > row_count:
        remaining = row_count % default_page_size
        remaining = remaining if remaining != 0 else default_page_size
        limit = offset + remaining

    limit = limit - offset

    if offset < 0:
        offset = 0

    return [total_pages, offset, limit]