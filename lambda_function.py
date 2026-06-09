import boto3, urllib.request, csv, io, os
from datetime import datetime, timezone

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    api_token = os.environ.get('API_TOKEN')
    api_url = f'https://www.pricecharting.com/price-guide/download-custom?t={api_token}'
    bucket_name = os.environ.get('BUCKET_NAME')
    today_str = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    s3_key = f'csv-landing/ingest_date={today_str}/snapshot.csv'

    # Indexes for columns in the CSV file with currency symbols - we want to remove these
    price_column_indexes = range(3, 20)

    try:
        req = urllib.request.Request(
            api_url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )

        with urllib.request.urlopen(req) as response:
            # Read data line by line using a text wrapper
            text_stream = io.TextIOWrapper(response, encoding='utf-8')
            csv_reader = csv.reader(text_stream)

            output_buffer = io.StringIO()
            csv_writer = csv.writer(output_buffer)

            # Process data row by row
            header = next(csv_reader)
            console_idx = header.index('console-name')
            csv_writer.writerow(header)

            # Consoles with active listings on Carousell. We want to filter on these.
            allowed_consoles = [
                "Wii",
                "Nintendo Switch",
                "Xbox 360",
                "Nintendo 64",
                "Gamecube",
                "Xbox One",
                "Nintendo DS",
                "Nintendo 3DS",
                "NES",
                "Playstation 3",
                "Xbox Series X",
                "Playstation 2",
                "Super Nintendo",
                "Xbox",
                "GameBoy Advance",
                "GameBoy",
                "Playstation",
                "Wii U",
                "GameBoy Color",
                "Nintendo Switch 2",
                "Playstation 4",
                "Playstation 5",
                "Sega Genesis",
                "Amiibo",
                "Sega Dreamcast",
                "PSP",
                "Game & Watch",
                "Atari 2600",
                "Playstation Vita",
                "Skylanders",
                "Strategy Guide",
                "Sega Saturn",
                "Lego Dimensions",
                "Sega Game Gear",
                "Sega 32X",
                "Intellivision",
                "Sega CD",
                "Disney Infinity",
                "Amiibo Cards",
                "TurboGrafx-16",
                "Virtual Boy",
                "Sega Master System",
                "Jaguar",
                "Neo Geo Pocket Color",
                "Evercade",
                "3DO",
                "Neo Geo MVS",
                "WonderSwan Color",
                "Starlink",
                "Mini Arcade",
                "Atari Lynx",
                "N-Gage",
                "Neo Geo AES",
                "WonderSwan",
                "PC FX",
                "Game Wave",
                "Pippin"
            ]

            for row in csv_reader:
                if row:
                    # Remove currency symbols from price columns
                    for idx in price_column_indexes:
                        if idx < len(row):
                            row[idx] = row[idx].replace('$', '')

                    if row[console_idx] in allowed_consoles:
                        csv_writer.writerow(row)

            clean_bytes = output_buffer.getvalue().encode('utf-8')

            # Upload to S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=clean_bytes
            )

            # Athena repair to include new data in table
            athena_client = boto3.client('athena')
            output_location = f's3://{bucket_name}/athena-queries/'
            athena_client.start_query_execution(
                QueryString=f'MSCK REPAIR TABLE pricecharting.prices;',
                QueryExecutionContext={'Database': 'pricecharting'},
                ResultConfiguration={'OutputLocation': output_location}
            )

        return {'statusCode': 200, 'body': f'Successfully saved file to {s3_key}'}

    except Exception as e:
        return {'statusCode': 500, 'body': str(e)}