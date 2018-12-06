f_in = open('ipfs_web_crawl_results.txt')
f_out = open('ipfs_web_crawl_hashes.txt', 'w')

hashes = set()

for result in f_in:
    print(result.strip())
    index = result.find('/ipfs/Qm')
    if index == -1:
        index = result.find('/ipfs/zb2')
    if index == -1:
        continue

    hash_path = result[index+len('/ipfs/'):].strip()
    slash_index = hash_path.find('/')
    q_index = hash_path.find('?')
    pound_index = hash_path.find('#')
    if slash_index != -1:
        ipfs_hash = hash_path[:slash_index]
    if q_index != -1:
        ipfs_hash = ipfs_hash[:q_index]
    if pound_index != -1:
        ipfs_hash = ipfs_hash[:pound_index]

    if len(ipfs_hash) < 25:
        continue

    if ipfs_hash not in hashes:
        print(ipfs_hash)
        hashes.add(ipfs_hash)

print(len(hashes))
for ipfs_hash in hashes:
    f_out.write(ipfs_hash + '\n')
