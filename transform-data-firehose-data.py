import base64         # Import the base64 module to encode and decode our data

def lambda_handler(event, context):       # The Entry point the AWS Lambda function calls when Firehose triggers this function
    output = []                           # We Initialised an empty list to store the transformed records

    for record in event['records']:                                       # This will Loop through each record in the batch sent by Firehose
        payload = base64.b64decode(record['data']).decode('utf-8')       # This will Decode the base64 encoded data into a readable string to allow appending a new line
        row_w_newline = payload + "\n"                                   # This will append a newline character so each record is on its own line in S3
        row_w_newline = base64.b64encode(row_w_newline.encode('utf-8')).decode('utf-8')    # Re-encode the transformed data back to base64 as Firehose requires it to always be in
        output_record = {                                                                 # The structure of the output response record Firehose expects back
            'recordId': record['recordId'],                              # This will return the original record ID unchanged so Firehose can match it 
            'result': 'Ok',                                              # This tells Firehose the transformation was successful
            'data': row_w_newline                                        # This returns the transformed base64 encoded data
            }
        output.append(output_record)                                     # This Adds the transformed record to the output list

    return {'records': output}                                           # This returns all the transformed records back to Firehose as a batch
 