import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Issuer } from '../models/issuer';
import { StepDependency } from '../models/step';

@Injectable({
  providedIn: 'root'
})
export class TobService {

  constructor(private http: HttpClient) { }

  /**
   * Returns the path - described as step and dependencies - to a step.
   * @param name The name of the shema being looked up.
   * @param version The version of the schema being looked up.
   * @param did The did of the issuer issuing the specified schema.
   */
  getPathToStep (name: string, version: string, did: string) {
    // TODO: need a way of determining the baseURL for an agent
    const baseURL = '/bcreg';
    const reqURL = `${baseURL}/get-credential-dependencies?schema_name=${name}&schema_version=${version}&origin_did=${did}`;
    // const reqURL = '/assets/data/topology.json';
    return this.http.post(reqURL, null);
  }

  /**
   * Queries ToB and returns a list of @Issuer entities that are currently registered.
   */
  getIssuers () {
    const reqURL = '/bc-tob/issuer?inactive=false&latest=true&revoked=false&page_size=250';
    // const reqURL = '/assets/data/issuers.json';
    // TODO: use types if possible
    return this.http.get(reqURL);
  }

  /**
   * Queries ToB and returns the list of @Schema objects that are currently registered.
   */
  getLatestSchemas () {
    const reqURL = '/bc-tob/schema?inactive=false&latest=true&revoked=false&page_size=250';
    // const reqURL = '/assets/data/schemas.json';
    // TODO: use types if possible
    return this.http.get(reqURL);
  }

  /**
   * Returns a JSON structure representing the requested topic (e.g.: Incorporated Company)
   * @param topicId the id of the topic being requested
   */
  getTopicById (topicId: number) {
    const reqURL = `/bc-tob/topic/${topicId}/formatted`;
    // const reqURL = '/assets/data/topic.json';
    // TODO: use types if possible
    return this.http.get(reqURL);
  }

  /**
   * Restirns a JSON structure representing the details for the credentials registered in ToB.
   */
  getCredentialTypes() {
    const reqURL = '/bc-tob/credentialtype?inactive=false&latest=true&revoked=false&page_size=250';
    return this.http.get(reqURL);
  }

  getCredentialsByTopic (topicId) {
    const reqURL = `/bc-tob/topic/${topicId}/credential/active`;
    // const reqURL = '/assets/data/credentials-by-topic.json';
    // TODO: use types if possible
    return this.http.get(reqURL);
  }

  /**
   * Returns the @Issuer matching the given did. If no issuer matches the DID, it returns null.
   * @param did the did of the issuer
   */
  getIssuerByDID (did: string, issuers: Array<Issuer>) {
    return issuers.find((issuer) => {
      return issuer.did === did;
    });
  }

  /**
   * Returns the list of @StepDependency for teh specified id.
   * @param id the id of the step being processed.
   * @param links the data structure representing the topology links.
   * @param creds the available credentials to be processed
   * @param issuers the list of issuers
   */
  getDependenciesByID (id: string, links: any, creds: any, issuers: Array<Issuer>) {
    return links.map((link) => {
      // straighten the tree: it is provided from the point of view of the destination,
      // we want it the other way around
      const newLink = {
        source: link.target,
        target: link.source
      };
      return newLink;
    }).filter((link) => {
      // find dependencies for this step: anywhere the link is a target
      return link.target === id;
    }).map((dep) => {
      // create new dep
      const depIssuer = issuers.find((issuer) => {
        return dep.source.indexOf(issuer.did) > -1
      });
      const isAvailable = this.isCredentialAvailable(dep.source, creds);
      const depSchema = dep.source.split(':')[0]; // ghrab the schema name
      return new StepDependency(depIssuer.name, depSchema, isAvailable);
    });
  }

  /**
   * Returns true if the credential corresponding to the given id if available, false otherwise.
   * @param id the id of the credential to check.
   * @param creds the list of credentials to check.
   */
  private isCredentialAvailable(id: string, creds: any) {
    const result = creds.filter((cred) => {
      return id.indexOf(cred.credential_type.issuer.did) > -1;
    });
    return result.length > 0;
  }
}
