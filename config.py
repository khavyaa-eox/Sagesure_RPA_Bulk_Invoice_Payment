# Chromedriver path
chrome_driver = "/home/eox_kavya/Sagesure/Sagesure_Celery/chromedriver-linux64/chromedriver"

# Snapsheet URLS
url = 'https://snapsheetvice.com/'

test_url = 'https://test.snapsheetvice.com/'

# Snapsheet Client Credentials
credentials = {
    'worker_0': [
        ('svc_claims_rpa+vendorbulkpay1@icg360.com', '>)N%VKC;>b[1H\k85,51'),
        ('svc_claims_rpa+vendorbulkpay2@icg360.com', 'A"]%6FY4q+B/8aN`E3nt')
    ],
    'worker_1': [
        ('svc_claims_rpa+vendorbulkpay3@icg360.com', '_3$FD^%UPwJs`53"$xsX'),
        ('svc_claims_rpa+vendorbulkpay4@icg360.com', '[]Im,^<v>|LW1$,>9|T_')
    ],
    'worker_2': [
        ('svc_claims_rpa+vendorbulkpay5@icg360.com', '1io$AU/XMz7NdV?5&kUN'),
        ('svc_claims_rpa+vendorbulkpay6@icg360.com', '($=,fosH(6#egR]By^=r')
    ],
    'worker_3': [
        ('svc_claims_rpa+vendorbulkpay7@icg360.com', "1,ENsoB,e@[&HN@;Rg'|"),
        ('svc_claims_rpa+vendorbulkpay8@icg360.com', '''BO;^A63lQM'"=(yG/kF}''')
    ]
}

# Ubuntu workers
# rpa-vendor-bulk-pay-worker-1 10.6.116.76
# rpa-vendor-bulk-pay-worker-2 10.6.117.237
# rpa-vendor-bulk-pay-worker-3 10.6.112.150

# S3 PATHS
s3_uploads_folder = 'rpa-vendor-bulk-pay/worker_1'
s3_processing_folder = 'rpa-vendor-bulk-pay/worker_1/processing_submissions'
s3_processed_folder = 'rpa-vendor-bulk-pay/worker_1/processed_submissions'
s3_error_folder = 'rpa-vendor-bulk-pay/worker_1/error_files'
s3_invalid_folder = 'rpa-vendor-bulk-pay/worker_1/invalid_submissions'

# LOCAL_PATHS
local_download_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/attachments/Input_Files'
local_error_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/Error_Files'
local_completed_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/Output Files'

# RDC_PATHS
download_path = '/attachments/Input_Files'
completed_path = '/Output Files'
error_path = '/Error_Files'