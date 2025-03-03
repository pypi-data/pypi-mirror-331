import { sharedUtils } from "./index";
import * as file from "./server/file";
import * as yaml from "./server/yaml";

export const serverUtils = {
    file,
    yaml,
};

export const Utils = {
    ...sharedUtils,
    ...serverUtils,
};
export default { ...Utils };
