import re

import pymongo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import sys
def track_request(service_provider, key_in_use, SKU, URL, status_code,request_type,request_limit,projectcode,feedid,developer_name):
    """
    Tracks the request by updating the count in MongoDB.

    :param conn_str: MongoDB connection string
    :param db_name: Database name
    :param collection_name: Collection (table) name
    :param service_provider: Static value declared by the user
    :param key_in_use: Static key declared by the user
    :param SKU: SKU identifier
    :param URL: URL being tracked
    :param status_code: Status code of the request
    :param request_type: Type of request (e.g., 'review', 'retry', etc.)
    """
    # project_name_new = projectcode.split(":")[1].split("]")[0]
    if ':' in projectcode:
        projectcode = projectcode.split(":")[1].split("]")[0]
    else:
        projectcode = projectcode.strip()
    db_name = f'xbyte_proxy_usage_{projectcode}'
    import datetime
    Date = datetime.date.today() + datetime.timedelta(days=0)
    TDate = Date.strftime("%Y_%m_%d")
    collection_name = f'{feedid}_{service_provider}_request_tracker_{TDate}'
    connmn = pymongo.MongoClient("mongodb://admin:tP_kc8-7$mn1@192.168.2.51:27017/?authSource=admin")
    mydb = connmn[db_name]
    collection = mydb[collection_name]
    key_in_use = key_in_use[-4:]

    # Fetch existing record
    record = collection.find_one({'SKU': SKU, 'URL': URL})
    review_count = record.get(request_type, 0) if record else 0

    new_count = review_count + 1
    if review_count == 0:
        collection.insert_one({
            'project_name': projectcode,
            'developer_name': developer_name,
            'key_in_use': f'xxxx{key_in_use}',
            'service_provider': service_provider,
            'SKU': SKU,
            'URL': URL,
            'status_code': status_code,
            request_type: new_count
        })
    else:
        collection.update_one(
            {'SKU': SKU, 'URL': URL},
            {'$set': {request_type: new_count}}
        )
    total_sum = sum(doc.get(request_type, 0) for doc in collection.find({}, {request_type: 1}))
    if total_sum >= request_limit:
        ################# Mail Generated #############

        try:
            mail_content = []
            mail_content.append("<html><head>")
            mail_content.append(
                """<style>table, th, td {border: 1px solid black; border-collapse: collapse;} 
                th, td {padding: 5px;} body {font-family: Verdana !important;}</style>"""
            )
            mail_content.append("</head><body><br>")

            mail_content.append("""<table><tbody><tr>""")
            mail_content.append("""<td style="background-color:#77D3EE; width:200px;"><b>Key In Use</b></td>""")
            mail_content.append("""<td style="background-color:#77D3EE; width:200px;"><b>Developer Name</b></td>""")
            mail_content.append("""<td style="background-color:#77D3EE; width:200px;"><b>Status Code</b></td>""")
            mail_content.append("""<td style="background-color:#77D3EE; width:200px;"><b>Count</b></td></tr>""")

            # Fetch all unique status codes along with key_in_use and developer_name
            pipeline = [{"$group": {"_id": {"status_code": "$status_code", "key_in_use": "$key_in_use",
                                            "developer_name": "$developer_name"}, "total_count": {"$sum": 1}}}]
            report_data = list(collection.aggregate(pipeline))

            if report_data:
                for row in report_data:
                    key_in_use = row["_id"].get("key_in_use", "N/A")
                    developer_name = row["_id"].get("developer_name", "N/A")
                    status_code = row["_id"].get("status_code", "N/A")
                    count = row["total_count"]

                    mail_content.append(f"""<tr>
                                    <td style="background-color:#FFFFFF; width:200px;">{key_in_use}</td>
                                    <td style="background-color:#FFFFFF; width:200px;">{developer_name}</td>
                                    <td style="background-color:#FFFFFF; width:200px;">{status_code}</td>
                                    <td style="background-color:#FFFFFF; width:200px;">{count}</td>
                                </tr>""")

            mail_content.append("</tbody></table>")
            mail_content.append("<p>This is system generated mail - Do Not Reply</p></body></html>")

            body = "".join(mail_content)
            # Email Configuration
            emailId = "alert.xbyte.internal@gmail.com"
            emailpass = "bkcadyrxpgrjyshx"
            send_to = ["forward.pc@xbyte.io"]
            cc = ["pruthak.acharya@xbyte.io", "bhavesh.parekh@xbyte.io", "anil.prajapati@xbyte.io"]
            # cc = ["dakshesh.bhardwaj@xbyte.io"]
            bcc = ["dakshesh.bhardwaj@xbyte.io"]
            from datetime import datetime
            try:
                msg = MIMEMultipart()
                msg['From'] = emailId
                msg['To'] = ",".join(send_to)
                msg['CC'] = ",".join(cc)
                msg['BCC'] = ",".join(bcc)
                msg['Subject'] = f"[Alert:{projectcode}] Proxy Usage Report : {datetime.now().strftime('%d/%m/%Y')}"
                msg.attach(MIMEText(body, 'html'))

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(emailId, emailpass)
                server.sendmail(emailId, send_to + cc + bcc, msg.as_string())
                server.quit()
                print("✅ Email Sent Successfully!")
            except Exception as e:
                print(f"❌ Error sending email: {e}")
        except Exception as e:
            print(e)
        ################### Limit Exceed #################
        input("Request limit reached! Press any key to exit...")
        print("Exiting program...")
        ########### Program Exit #########
        sys.exit()

if __name__ == '__main__':
    track_request('scraper','xxxxxxxxxxxxxxxxxxxxxxxxx794abd','B0CKZCX4D7','https://www.amazon.com/dp/B0CKZCX4D7',200,'review_retry_count',1,'2762','8277','Bhumika Bhatti')