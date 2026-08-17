/** Companies House company, officer, PSC, charge and filing data. */

import { seg, type QueryParams, type Transport } from '../transport.js';
import type { JsonObject } from '../types.js';

/** Options accepted by every call: cancellation via an `AbortSignal`. */
export interface CallOptions {
  signal?: AbortSignal;
}

export interface PageOptions extends CallOptions {
  /** Page size. The API applies its own default and cap. */
  itemsPerPage?: number;
  /** Zero-based offset for paging. */
  startIndex?: number;
}

export interface FilingHistoryOptions extends PageOptions {
  /** Companies House filing category, e.g. `"accounts"`, `"confirmation-statement"`. */
  category?: string;
}

/** Filters for {@link Companies.advancedSearch}. Dates are `YYYY-MM-DD`. */
export interface AdvancedSearchOptions extends PageOptions {
  companyNameIncludes?: string;
  companyNameExcludes?: string;
  /** Repeatable: `["active", "liquidation"]` matches either. */
  companyStatus?: string[];
  companyType?: string[];
  location?: string;
  sicCodes?: string[];
  incorporatedFrom?: string;
  incorporatedTo?: string;
  dissolvedFrom?: string;
  dissolvedTo?: string;
  size?: number;
}

/**
 * Company registry lookups. Available on every plan.
 *
 * Company numbers are Companies House registration numbers — up to eight
 * alphanumeric characters, e.g. `"00445790"` or `"SC123456"`. Leading zeroes are
 * significant, so keep them as strings.
 */
export class Companies {
  constructor(private readonly transport: Transport) {}

  /** Search companies by name or number. */
  async search(q: string, options: PageOptions = {}): Promise<JsonObject> {
    return this.transport.get('/companies/search', {
      params: { q, items_per_page: options.itemsPerPage, start_index: options.startIndex },
      signal: options.signal,
    });
  }

  /** Search officers (directors, secretaries) by name across all companies. */
  async searchOfficers(q: string, options: PageOptions = {}): Promise<JsonObject> {
    return this.transport.get('/companies/search/officers', {
      params: { q, items_per_page: options.itemsPerPage, start_index: options.startIndex },
      signal: options.signal,
    });
  }

  /** Structured company search with status, type, SIC and date filters. */
  async advancedSearch(options: AdvancedSearchOptions = {}): Promise<JsonObject> {
    const params: QueryParams = {
      company_name_includes: options.companyNameIncludes,
      company_name_excludes: options.companyNameExcludes,
      company_status: options.companyStatus,
      company_type: options.companyType,
      location: options.location,
      sic_codes: options.sicCodes,
      incorporated_from: options.incorporatedFrom,
      incorporated_to: options.incorporatedTo,
      dissolved_from: options.dissolvedFrom,
      dissolved_to: options.dissolvedTo,
      size: options.size,
      start_index: options.startIndex,
      items_per_page: options.itemsPerPage,
    };
    return this.transport.get('/companies/advanced-search', { params, signal: options.signal });
  }

  /** The company profile: name, status, type, dates, address, SIC codes. */
  async get(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(`/companies/${seg(companyNumber, 'companyNumber')}`, options);
  }

  /**
   * Profile, officers, PSCs, charges, insolvency and filings in one call.
   *
   * Cheaper than issuing each lookup separately — one request against your rate
   * limit instead of six.
   */
  async dossier(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(`/companies/${seg(companyNumber, 'companyNumber')}/dossier`, options);
  }

  /** Appointed officers, including resigned ones. */
  async officers(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/officers`,
      options,
    );
  }

  /** Registered beneficial owners (PSCs). */
  async pscs(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/persons-with-significant-control`,
      options,
    );
  }

  /** PSC statements — the register's explanations for an absent PSC. */
  async pscStatements(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/persons-with-significant-control-statements`,
      options,
    );
  }

  /** How many corporate layers sit between the company and a real person. */
  async pscChainDepth(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/psc-chain-depth`,
      options,
    );
  }

  /** The full ownership chain as a tree, resolving corporate PSCs upwards. */
  async pscChainTree(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/psc-chain-tree`,
      options,
    );
  }

  /** Registered charges (secured debt) against the company. */
  async charges(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(`/companies/${seg(companyNumber, 'companyNumber')}/charges`, options);
  }

  /** One charge in full, including the persons entitled to it. */
  async charge(
    companyNumber: string,
    chargeId: string,
    options: CallOptions = {},
  ): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/charges/${seg(chargeId, 'chargeId')}`,
      options,
    );
  }

  /** Insolvency cases. Returns an empty payload when there are none. */
  async insolvency(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/insolvency`,
      options,
    );
  }

  /** Disqualified-director records across the company's officers. */
  async disqualifications(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/disqualifications`,
      options,
    );
  }

  /** Disqualification record for one officer of this company. */
  async officerDisqualification(
    companyNumber: string,
    officerId: string,
    options: CallOptions = {},
  ): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/officers/${seg(officerId, 'officerId')}/disqualification`,
      options,
    );
  }

  /** Every appointment held by one officer, across all companies. */
  async officerAppointments(officerId: string, options: PageOptions = {}): Promise<JsonObject> {
    return this.transport.get(`/companies/officers/${seg(officerId, 'officerId')}/appointments`, {
      params: { items_per_page: options.itemsPerPage, start_index: options.startIndex },
      signal: options.signal,
    });
  }

  // ── Professional plan ──────────────────────────────────────────────────────

  /** Filing history. **Requires an active Professional subscription.** */
  async filingHistory(
    companyNumber: string,
    options: FilingHistoryOptions = {},
  ): Promise<JsonObject> {
    return this.transport.get(`/companies/${seg(companyNumber, 'companyNumber')}/filing-history`, {
      params: {
        start_index: options.startIndex,
        items_per_page: options.itemsPerPage,
        category: options.category,
      },
      signal: options.signal,
    });
  }

  /**
   * Structured data parsed out of one filing.
   *
   * **Requires an active Professional subscription.**
   */
  async filingExtract(
    companyNumber: string,
    transactionId: string,
    options: CallOptions = {},
  ): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/filing-history/${seg(transactionId, 'transactionId')}/extract`,
      options,
    );
  }

  /**
   * Share capital and shareholders from the latest confirmation statement.
   *
   * **Requires an active Professional subscription.**
   */
  async statementOfCapital(companyNumber: string, options: CallOptions = {}): Promise<JsonObject> {
    return this.transport.get(
      `/companies/${seg(companyNumber, 'companyNumber')}/statement-of-capital`,
      options,
    );
  }
}
