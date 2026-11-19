# Offline workflows

The implemented deterministic offline command is:

> Find the newest PDF in Downloads, copy it to Documents, open the copy, and tell me where you saved it.

It performs no network operation. It accepts equivalent punctuation/capitalization but deliberately rejects unrelated natural language instead of guessing.

The engine can also receive typed `copy_file` actions from a trusted deterministic adapter. All paths must remain inside configured permitted roots.

Browser commands and cloud-only data are not implemented yet. When added, they must report a clear connectivity requirement before attempting network access.

