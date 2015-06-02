import fileinput
import json


if __name__ == '__main__':
  tags = set()
  json_string = '\n'.join(fileinput.input())
  site_list = json.loads(json_string)
  for site_dict in site_list:
    tags |= set(site_dict['element_hist'].keys())

  tags = list(tags)
  # Header.
  print('url,{}'.format(','.join(tags)))
  for site_dict in site_list:
    tag_counts = []
    for tag in tags:
      tag_counts.append(site_dict['element_hist'].get(tag, 0))

    tag_counts = map(str, tag_counts)
    print('{},{}'.format(site_dict['url'], ','.join(tag_counts)))
