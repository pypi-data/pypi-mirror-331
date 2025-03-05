import datetime

from .utils import extract_column


class TrendsDataConverter:

    @staticmethod
    def token_to_bullets(token_data):
        items = token_data.get('request', {}).get('comparisonItem', [])
        bullets = [
            item.get('complexKeywordsRestriction', {}).get('keyword', [''])[0].get('value', '')
            for item in items
        ]
        metadata = [next(iter(item.get('geo', {'': 'unk'}).values()), 'unk') for
                    item in items]
        if len(set(metadata)) > 1:
            bullets = [b + ' | ' + m for b, m in zip(bullets, metadata)]
        metadata = [item.get('time', '').replace('\\', '') for item in items]
        if len(set(metadata)) > 1:
            bullets = [b + ' | ' + m for b, m in zip(bullets, metadata)]

        return bullets

    @staticmethod
    def interest_over_time(widget_data, keywords, time_as_index=True):
        timeline_data = widget_data.get('default', {}).get('timelineData', [])
        if not timeline_data:
            return []

        include_partial = ('isPartial' in timeline_data[-1]) \
            or any('isPartial' in row for row in timeline_data)
        res = []

        for row in timeline_data:
            keywords_data = dict(zip(keywords, row['value']))
            timestamp = int(row['time']) if row.get('time', None) else None
            time = datetime.datetime.fromtimestamp(
                timestamp) if timestamp else None
            obj = {
                'time': time,
                **keywords_data,
            }
            if include_partial:
                obj['isPartial'] = row.get('isPartial', None)

            res.append(obj)

        return res

    @staticmethod
    def multirange_interest_over_time(data, bullets=None):
        timeline_data_list = data.get('default', {}).get('timelineData', [{}])
        if not timeline_data_list or 'columnData' not in timeline_data_list[0]:
            return []  # No valid timeline data found

        num_parts = len(timeline_data_list[0]['columnData'])
        if bullets is None:
            bullets = ['keyword_' + str(i) for i in range(num_parts)]

        columns_data = {}
        num_rows = len(timeline_data_list)

        for i in range(num_parts):
            part_data = [entry['columnData'][i] for entry in timeline_data_list]
            values = extract_column(part_data, 'value', None, f=lambda x: x if x != -1 else None)
            columns_data[bullets[i]] = values

            needs_partial = ('isPartial' in part_data[-1]) or \
                any('isPartial' in row for row in part_data)

            if needs_partial:
                is_partials = extract_column(part_data, 'isPartial', False)
                columns_data['isPartial_' + str(i)] = is_partials

            # Extract and convert the 'time' column. Convert each timestamp (assumed in seconds) into a datetime.
            times = extract_column(part_data, 'time', None, f=lambda ts: int(ts) if ts else None)
            times = [
                datetime.datetime.fromtimestamp(ts) if ts is not None else None
                for ts in times]
            columns_data['index_' + str(i)] = times

        # Assemble the result as a list of dictionaries, one per row.
        result_table = []
        for row_idx in range(num_rows):
            row = {}
            for col_name, col_values in columns_data.items():
                row[col_name] = col_values[row_idx]
            result_table.append(row)

        return result_table
