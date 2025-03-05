transform_date_dashed_to_nodashed = lambda date_str: date_str.replace('-', '')

transform_date_nodashed_to_dashed = lambda date_str: f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

map_date_dashed_to_nodashed = transform_date_dashed_to_nodashed
map_date_nodashed_to_dashed = transform_date_nodashed_to_dashed