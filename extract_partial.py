import os

src_file = r'd:\balilihan_waterworks\waterworks\consumers\templates\consumers\consumer_list.html'
with open(src_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

table_lines = lines[146:360]

out_dir = r'd:\balilihan_waterworks\waterworks\consumers\templates\consumers\partials'
os.makedirs(out_dir, exist_ok=True)
out_file = os.path.join(out_dir, 'consumer_table_only.html')

with open(out_file, 'w', encoding='utf-8') as f:
    f.writelines(table_lines)

new_lines = lines[:146] + [
    '    <div id="consumer-results">\n',
    '        {% include "consumers/partials/consumer_table_only.html" %}\n',
    '    </div>\n'
] + lines[360:]

with open(src_file, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
