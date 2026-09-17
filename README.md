# Serverless Data Analytics Solution Pipeline on AWS

This repository contains step-by-step instructions for designing and deploying a serverless data analytics solution on AWS. 

The solution enables a customer's AWS infrastructure to ingest, store, process, and visualize real-time clickstream data from their website. 

This customer is a fast-food business owner who wants to gain insights into ordered menu items while adhering to strict data regulatory requirements by ensuring all data stays within the eu-north-1 (Stockholm) region.


## KEY ARCHITECTURAL COMPONENTS

INGESTION: Amazon API Gateway	acts as the front-door service for client requests from the fast-food website, accepting clickstream data and securely routing it to the backend.

STREAM PROCESSING: Amazon Kinesis Data Firehose	provides near real-time data delivery by ingesting streaming data from API Gateway and reliably loading it into Amazon S3.

DATA TRANSFORMATION:	AWS Lambda triggered by Kinesis Firehose to clean and transform raw ingested data (e.g., adding newlines) before it is permanently stored in S3.

STORAGE (DATA LAKE):	Amazon Simple Storage Service (S3) serves as the centralized, scalable, and secure online storage locker for all streaming data.

INTERACTIVE QUERYING: Amazon Athena	enables running ad-hoc SQL queries directly on files sitting in the S3 bucket without needing to set up or manage servers.

DATA VISUALIZATION: Amazon QuickSight turns raw data and Athena query results into interactive, visual dashboards to identify trends and outliers.

### PDF GUIDE: [DESIGN A SERVERLESS DATA ANALYTICS SOLUTION ON AWS.pdf](https://github.com/user-attachments/files/32198691/DESIGNNING.A.SERVERLESS.DATA.ANALYTICS.SOLUTION.ON.AWS.pdf)

### WATCH VIDEO WALKTHROUGH HERE: https://youtu.be/e7dfyrv-690


## DEPLOYMENT INSTRUCTIONS

Follow these step-by-step instructions to implement the serverless analytics infrastructure.

Warning: To maintain regulatory compliance, ensure all services are deployed within the eu-north-1 (Stockholm) region.

For multi-region disaster recovery, the customer would have to proffer a solution for that in the future.


### Step 1: Create IAM Security Policy for Kinesis Data Firehose

Create an IAM policy that grants permissions to write records to the Kinesis Data Firehose delivery stream.

1) Navigate to the IAM Console -> Policies -> Create Policy.

2) Switch to the JSON tab and replace the default code with the policy in the API-firehose-policy.json file:

3) Click **Next**.

4)  **Policy Name:** `API-Firehose`

5)  **Description:** `This policy allows Kinesis Data Firehose to receive data.`
   
6)  Click **Create Policy**.


### Step 2: Create IAM Role for API Gateway Ingestion

Create an IAM role enabling API Gateway to send clickstream data to Kinesis Data Firehose and attach the `API-Firehose` policy.

1)  Navigate to **IAM Console** -> **Roles** -> **Create Role**.

2)  **Trusted Entity Type:** `AWS Service`

3)  **Use Case:** `API Gateway`

4)  Click **Next** -> **Next**.

5)  **Role Name:** `APIGateway-Firehose`

6)  Click **Create Role**.

7)  Search for and click on `APIGateway-Firehose`.

8)  Under the **Permissions** tab, click **Add Permissions** -> **Attach Policies**.

9)  Search for and check the box next to `API-Firehose`, then click **Add Permissions**.

10) Verify that both standard AWS managed policies and the custom `API-Firehose` policy are attached.


### Step 3: Create the S3 Bucket for Data Lake Storage

Create a globally unique S3 bucket to store the streaming data.

1)  Navigate to **Amazon S3 Console** -> **Create Bucket**.

2)  **Region:** Ensure `eu-north-1` (Stockholm) is selected.

3)  **Bucket Name:** *[cite: Your-Globally-Unique-Bucket-Name]* (e.g., `data-lake-1400-bucket`).

4)  Leave other default settings and click **Create Bucket**.

5)  Click your bucket name in the list, navigate to the **Properties** tab, copy the **Bucket ARN**, and paste it for later use. (Format: `arn:aws:s3:::bucket-name`)


### Step 4: Create the AWS Lambda Data Transformation Function

Create a Lambda function to transform ingested data before delivery to S3. 
The transformation code ensures each record ends with a newline character for improved readability.

1)  Navigate to **AWS Lambda Console** -> **Create Function**.

2)  Select **Use a blueprint**.

3)  Search for and select **Process records sent to an Amazon Data Firehose stream (Python)** (e.g., Python 3.12).

4)  **Function Name:** `transform-data-firehose-data`

5)  Click **Create Function**.

6)  Under the **Code** tab, navigate to the **Explorer** pane, open `lambda_function.py`, and replace the existing code with the code in the `transform-data-firehose-data.py` file:

7)  Click **Deploy**.

8)  Go to the **Configuration** tab -> **General Configuration** -> **Edit**.

9)  Increase **Timeout** to `10 seconds` to accommodate high traffic volume.

10) Click **Save**.

11) Scroll up, copy the **Function ARN**, and paste it for later use


### Step 5: Create and Configure Kinesis Data Firehose

Create a Kinesis Firehose delivery stream to ingest raw data and deliver transformed data to S3. You must update the S3 bucket policy to grant Firehose write permissions.

1)  Navigate to **Amazon Kinesis Console** -> **Create Firehose Stream**.

2)  **Source:** `Direct PUT`

3)  **Destination:** `Amazon S3`

4)  **Firehose Stream Name:** `click-stream-api-gateway-data-ingestion`

5)  Under **Transform, and convert records - optional**, enable **Turn on data transformation**.

6)  **AWS Lambda Function:** Paste the ARN of the `transform-data-firehose-data` function and select the `LATEST` version.

7)  Under **Destination Settings**, click **Browse** and select your created S3 bucket (e.g., `data-lake-1400-bucket`).

8)  Leave other defaults and click **Create Firehose Stream**.

9)  After creation, copy the **Firehose Stream ARN** and paste it for later use.

10) Under the **Configuration** tab -> **Service access**, click the link to open the IAM role used by Firehose.

11) Copy the **Role ARN** and paste it.

#### Update your S3 Bucket Policy

Grant the Kinesis Firehose role permission to write data into your S3 bucket.

12)  Navigate back to your S3 bucket console.

13)  Go to the **Permissions** tab -> **Bucket Policy** -> **Edit**.

14)  use the policy from s3_bucket_policy.json replacing `<Your_Kinesis_Firehose_Role_ARN>` and `<Your_S3_Bucket_ARN>` with your recorded ARNs:

15)  Click **Save Changes**


### Step 6: Create API Gateway to Ingest Clickstream Data

Create a REST API that serves as a communication gateway between the client website and Kinesis Data Firehose.

1)  Navigate to **Amazon API Gateway Console** -> **Create API**.

2)  Select **REST API** (Build).

3)  **API Name:** `ingest-data-from-clickstream-into-kinesis-data-firehose`

4)  Click **Create API**.

5)  **Create Resource:** Name it `url-link`. This generates the URL link for data imputation.

6)  Under **Methods**, click **Create Method**.

7)  **Method Type:** `POST`

8)  **Integration Type:** `AWS Service`

9)  **AWS Service:** `firehose`

10) **HTTP Method:** `POST`

11) **Action Type:** `Use action name`

12) **Action Name:** `PutRecord`

13) **Execution Role:** Paste the ARN of the `APIGateway-Firehose` role created in Step 2.

14) Click **Create Method**.

#### Configure VTL Mapping Template

API Gateway uses a Velocity Template Language (VTL) mapping template to transform the incoming clickstream JSON structure to fit the expected Kinesis Data Firehose format.

15)  In the API Gateway Resources dashboard, navigate to the **Integration Request** tab -> **Edit**.
    
16)  Go to **Mapping Templates** -> **Add Mapping Template**.

17)  **Content Type:** `application/json`

18) In the template body, paste the following snippet, replacing `<Enter_your_delivery_stream_name>` with your actual Firehose stream name (also available in `api_gateway_mapping_template.vtl` in this repo):

```vtl
{
  "DeliveryStreamName": "<Enter_your_delivery_stream_name>",
  "Record": {
    "Data": "$util.base64Encode($util.escapeJavaScript($input.json('$')).replace('\', ''))"
  }
}
```

19)  Set **Request body passthrough** to `When there are no templates defined (recommended)`.

20)  Click **Save**.


## INGESTION TESTING AND VERIFICATION

To ensure the infrastructure is working correctly, simulate clickstream events and verify they persist in S3.

1)  In the API Gateway Resource page, navigate to the **Test** tab.

2)  In the request body, paste the following JSON payload simulating a menu item selection and click **Test**:

```json
{
  "element_clicked": "entree_1",
  "time_spent": 12,
  "source_menu": "restaurant_name",
  "created_at": "2025-09-11 23:00:00"
}
```

3) Verify the **Request Logs**: Look for **status 200** at the top and `Received response. Status: 200` in the middle, indicating successful processing by API Gateway and transformation by Firehose.

4) Perform additional tests by submitting the payloads below in succession:

   ```json
   {
     "element_clicked": "entree_4",
     "time_spent": 32,
     "source_menu": "restaurant_name",
     "createdAt": "2025–09–11 23:00:00"
   }
   ```

   ```json
   {
     "element_clicked": "drink_1",
     "time_spent": 15,
     "source_menu": "restaurant_name",
     "created_at": "2022–09–11 23:00:00"
   }
   ```

   ```json
   {
     "element_clicked": "drink_3",
     "time_spent": 14,
     "source_menu": "restaurant_name",
     "created_at": "2022–09–11 23:00:00"
   }
   ```

5) Confirm that each test results in a **status 200**.

6) Navigate to your **Amazon S3 Bucket** (Objects tab). Keep refreshing until you see a folder structure like `YYYY/` corresponding to the year the data was created.
   Due to Kinesis Data Firehose latency, this can take several minutes.


## DATA QUERYING AND VISUALIZATION

### Step 7: Create and Query Data via Amazon Athena

Set up Amazon Athena to query data stored in S3 using Structured Query Language (SQL).

1) Navigate to the **Amazon Athena Console**.

2) Click **Launch query editor**.

3) Click the **Query settings** tab -> **Manage**.

4) Under **Query result location**, browse to and select your S3 bucket. Append `/results/` to create a sub-folder for Athena query results.
   Example: `s3://data-lake-1400-bucket/results/`

5)  Click **Save** and return to the **Editor** tab.

6)  Create an external partitioned table, use the Anthena_Query.sql provided in this repo replacing both instances of `<Enter_your_Amazon_S3_bucket_name>` with your actual bucket name:

7)  Click **Run**. Verify the **Query successful** message and confirm the table appears in the **Tables** list.

8)  Run a SQL query to view the ingested clickstream data:
   ```sql
   SELECT * FROM my_ingested_clickstream_data;
   ```


### Step 8: Build an Amazon QuickSight Dashboard

Create a cloud-based business intelligence (BI) dashboard to visualize trend insights from the clickstream data.

1) Navigate to the **Amazon QuickSight Console**.

2) New users must complete the sign-up process, ensuring the default region is set to `Europe(Stockholm)` (`eu-north-1`) for Europe(Stockholm) to match data lake storage.

3) Click the **User icon** at the top right -> **Manage QuickSight**.

4) Navigate to **AWS resources** -> select **Amazon S3** -> check the box next to your bucket (e.g., `data-lake-1400-bucket`) -> click **Finish** -> click **Save**.
    This grants QuickSight necessary S3 permissions.
    
5) Return to the **Analyses** tab -> **Create analysis** -> **Create dataset** -> **Create data source**.

6) Select **Amazon Athena**, click **Next**, give your data source a name (e.g., `clickstream_data`), and click **Create data source**.

7) Select the `my_ingested_clickstream_data` table you created in Athena and click **Select**.

8)  Leave default settings and click **Visualize**.

9)  Start analyzing data by dragging fields from the table into the interactive charts on the analysis page.

> **Tip:** Visit the official QuickSight documentation on AWS to learn how to create advanced interactive dashboards.


## Step 9: Service Teardown and Resource Cleanup

To avoid incurring future charges, ensure you delete all AWS services and accounts created during this exercise.

1) **Amazon QuickSight:**
    *   Delete datasets and data sources.
    *   Navigate to **Manage QuickSight** -> **Account Settings** -> under **Account termination** click **Manage** -> disable termination protection -> delete account.

2)  **Amazon S3:** Empty and delete the data lake bucket and results subfolder.

3)  **Amazon Athena:** Delete the created SQL table.

4)  **Amazon API Gateway:** Delete the REST API.

5)  **Amazon Kinesis Data Firehose:** Delete the delivery stream.

6)  **AWS Lambda:** Delete the data transformation function.



