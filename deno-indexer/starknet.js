/* Starknet ETH indexer
 *
 * This file contains a filter and transform to index Starknet ETH transactions.
 */

// You can import any library supported by Deno.
import { hash, uint256 } from "https://esm.run/starknet@5.14";
import { formatUnits } from "https://esm.run/viem@1.4";

const DECIMALS = 18;
// Can read from environment variables if you want to.
// In that case, run with `--env-from-file .env` and put the following in .env:
// TOKEN_DECIMALS=18
// const DECIMALS = Deno.env.get('TOKEN_DECIMALS') ?? 18;

export const filter = {
  // Only request header if any event matches.
  header: {
    weak: true,
  },
  events: [
    {
      fromAddress:
        "0x0603c4273d547ecfccc3c89bcfce9a11b454e0acb9a1c22166846cfda1ad7756",
      keys: [
        hash.getSelectorFromName("OrganisationCreated"),
      ],
      includeReceipt: false,
    },
  ],
};

export function decodeTransfersInBlock({ header, events }) {
  const { blockNumber, blockHash, timestamp } = header;
  return events.map(({ event, transaction }) => {
    const transactionHash = transaction.meta.hash;
    const orgCreatationId = `${transactionHash}_${event.index}`;

    const [name, org, metadata, id] = event.data;

    // Convert to snake_case because it works better with postgres.
    return {
      network: "starknet-sepolia",
      symbol: "ETH",
      block_hash: blockHash,
      block_number: +blockNumber,
      block_timestamp: timestamp,
      transaction_hash: transactionHash,
      org_creation_id: orgCreatationId,
      name: name,
      org: org,
      metadata: metadata,
      id: id,
    };
  });
}