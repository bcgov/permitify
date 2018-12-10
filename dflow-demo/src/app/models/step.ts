import { Issuer } from './issuer';

export class Step {
  // mandatory
  topicId: number;
  name: string;
  dependencies: Array<StepDependency>;

  // optional
  issuer: Issuer;
  effectiveDate: string;
  credentialId: number;
  walletId: string;
  // TODO: refactor requestedschema out of the step, if possible
  requestedSchema: any;
  actionURL: string;

  // computed
  actionText: string;

  constructor ( stepData: any ) {
      this.topicId = stepData.topicId;
      this.walletId = stepData.walletId;
      this.name = stepData.stepName;
      this.dependencies = stepData.dependencies;
      this.issuer = stepData.issuer;
      if (stepData.credData) {
        this.credentialId = stepData.credData.id;
        this.effectiveDate = stepData.credData.effective_date;
      }
      this.actionURL = stepData.schemaURL;

      this.requestedSchema = {
        name: '',
        version: '',
        did: ''
      }
      if (stepData.schema) {
        this.requestedSchema.name = stepData.schema.name;
        this.requestedSchema.version = stepData.schema.version;
        this.requestedSchema.did = stepData.schema.did;
      }
    }
}

export class StepDependency {
  name: string;
  schema: string;
  isAvailable: boolean;

  constructor (name: string, schema: string, isAvailable = false) {
    this.name = name;
    this.schema = schema;
    this.isAvailable = isAvailable;
  }
}
