import csv
import xml.etree.ElementTree as ET
from pathlib import Path

# Base directory containing the .rdl files
base_path = Path(r'C:\Users\MohammadAli\Downloads\AKReports\Reports')
output_rows = []

def extract_namespace(tag):
    """Extract XML namespace from root tag"""
    if tag.startswith("{"):
        return {'ns': tag[1:].split("}")[0]}
    return {}

def parse_rdl_file(file_path, relative_dir):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        ns = extract_namespace(root.tag)

        data_sources = root.find('ns:DataSources', ns)
        if data_sources is not None:
            found = False
            for ds in data_sources.findall('ns:DataSource', ns):
                name = ds.attrib.get('Name', '')
                ref = ds.find('ns:DataSourceReference', ns)
                sec = ds.find('ns:ConnectionProperties/ns:SecurityType', ns)

                output_rows.append({
                    'Report Name': file_path.name,
                    'Report Path': str(relative_dir),
                    'Data Source Name': name,
                    'Data Source Reference': ref.text if ref is not None else '',
                    'Data Source Security': sec.text if sec is not None else '',
                    'Status': 'Extracted'
                })
                found = True

            if not found:
                append_no_data(file_path.name, relative_dir, 'No DataSources Found')
        else:
            append_no_data(file_path.name, relative_dir, 'No DataSources Tag')

    except Exception as e:
        append_no_data(file_path.name, relative_dir, f'Error: {str(e)}')

def append_no_data(report_name, report_path, status):
    output_rows.append({
        'Report Name': report_name,
        'Report Path': str(report_path),
        'Data Source Name': '',
        'Data Source Reference': '',
        'Data Source Security': '',
        'Status': status
    })

# Walk through all RDL files
for rdl_file in base_path.rglob("*.rdl"):
    relative_dir = rdl_file.relative_to(base_path).parent
    parse_rdl_file(rdl_file, relative_dir)

# Write output CSV
output_file = base_path / 'rdl_report_metadata_with_status.csv'
with output_file.open('w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'Report Name',
        'Report Path',
        'Data Source Name',
        'Data Source Reference',
        'Data Source Security',
        'Status'
    ])
    writer.writeheader()
    writer.writerows(output_rows)

print(f"[✓] Metadata successfully written to: {output_file}")
