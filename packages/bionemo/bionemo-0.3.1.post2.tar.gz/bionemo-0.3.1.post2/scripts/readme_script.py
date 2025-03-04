from time import sleep

from bionemo.api import BionemoClient

# Create a client instance
api = BionemoClient()

# Generate novel proteins
novel_proteins = api.protgpt2_sync(max_length=200, num_return_sequences=5)

# Request folding of novel proteins in parallel
submitted_requests = []
for protein in novel_proteins["generated_sequences"]:
    request_id = api.request_openfold(protein)
    submitted_requests.append(request_id)

# Wait for results, write to disk
while len(submitted_requests):
    sleep(10)
    print(submitted_requests)
    for request_id in submitted_requests:
        if api.fetch_task_status(request_id) == "DONE":
            print("{} hit!".format(request_id))
            folded_protein = api.fetch_result(request_id)
            with open(str(request_id) + ".pdb", "w") as f:
                f.write(folded_protein)
            submitted_requests.remove(request_id)
