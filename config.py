# Chromedriver path
chrome_driver = ""

# Snapsheet URLS
url = 'https://snapsheetvice.com/'

test_url = 'https://test.snapsheetvice.com/'

# Snapsheet Client Credentials
credentials = {
    'worker_1': [
        ('svc_claims_rpa+vendorbulkpay3@icg360.com', 'f?p8q>ExrOT7Y%WB=(F::'),
        ('svc_claims_rpa+vendorbulkpay4@icg360.com', 'P_:-I?>X:!pVsOsy2gAzz')
    ],
    'worker_2': [
        ('svc_claims_rpa+vendorbulkpay5@icg360.com', 't#lXB7t)*=lDh[0DQ^?PP'),
        ('svc_claims_rpa+vendorbulkpay6@icg360.com', 'L-IC[#@YTwp1y}T9UK;77')
    ],
    'worker_3': [
        ('svc_claims_rpa+vendorbulkpay7@icg360.com', 'f7C0Es+hR+0x,Jyt$t$11'),
        ('svc_claims_rpa+vendorbulkpay8@icg360.com', 'd|q3|984%E8&L2{ih?dDD')
    ]
}

# Ubuntu workers
# rpa-vendor-bulk-pay-worker-1 10.6.116.76
# rpa-vendor-bulk-pay-worker-2 10.6.117.237
# rpa-vendor-bulk-pay-worker-3 10.6.112.150

target_worker = "worker_1"

# S3 PATHS
s3_uploads_folder = 'rpa-vendor-bulk-pay/worker_3'
s3_processing_folder = 'rpa-vendor-bulk-pay/worker_3/processing_submissions'
s3_processed_folder = 'rpa-vendor-bulk-pay/worker_3/processed_submissions'
s3_error_folder = 'rpa-vendor-bulk-pay/worker_3/error_files'
s3_invalid_folder = 'rpa-vendor-bulk-pay/worker_3/invalid_submissions'

# LOCAL_PATHS
local_download_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/attachments/input_files'
local_error_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/error_files'
local_completed_path = '/home/eox_kavya/Sagesure_RPA_Bulk_Invoice_Payment/output_files'

# RDC_PATHS
download_path = '/home/rpa-user/Sagesure_RPA_Bulk_Invoice_Payment/attachments/input_files'
completed_path = '/home/rpa-user/Sagesure_RPA_Bulk_Invoice_Payment/output_files'
error_path = '/home/rpa-user/Sagesure_RPA_Bulk_Invoice_Payment/error_files'


