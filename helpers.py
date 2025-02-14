def _convert_data(self, row):
        """Convertit les types de données pour correspondre aux types natifs."""
        for key, value in row.items():
            if value.isdigit():
                row[key] = int(value)
            elif value.replace('.', '', 1).isdigit():
                row[key] = float(value)
            elif value.lower() == 'true':
                row[key] = True
            elif value.lower() == 'false':
                row[key] = False
            elif value.startswith("[") and value.endswith("]"):
                row[key] = eval(value) 
        return row