import collections

import fileinput
import json
import re

from tags import TAGS, SEMANTIC_TAGS


if __name__ == '__main__':
  json_string = '\n'.join(fileinput.input())
  site_list = json.loads(json_string)

  # Header.
  print('site_url,total_tags,valid_tags,semantic_tags,semantic_tag_frac,{}'.format(','.join(TAGS)))

  for site_dict in site_list:
    url = site_dict['url']
    match = re.match(r'(https?://[\w.]+).*', url)

    if not match:
      continue

    url = match.group(1) + '/'

    total_tags = sum(site_dict['element_hist'].values())

    valid_tags = 0
    semantic_tags = 0
    tag_counts = []
    for tag in TAGS:
      count = site_dict['element_hist'].get(tag, 0)
      tag_counts.append(count)

      valid_tags += count

      if tag in SEMANTIC_TAGS:
        semantic_tags += count

    semantic_tag_frac = 1. * semantic_tags / valid_tags

    cols = [url,
            total_tags, valid_tags,
            semantic_tags, semantic_tag_frac] + tag_counts

    cols = map(str, cols)
    print(','.join(cols))
