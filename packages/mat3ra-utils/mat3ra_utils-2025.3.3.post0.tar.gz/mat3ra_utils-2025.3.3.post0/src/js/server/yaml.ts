import fs from "fs";

import { convertJSONToYAMLString, convertYAMLStringToJSON } from "../shared/yaml";

/**
 * Reads a YAML file and converts its content to a JSON object.
 * @param {string} filePath - The path to the YAML file.
 * @returns {object} - The resulting JSON object.
 */
export function readYAMLFile(filePath: string): object {
    const YAMLContent = fs.readFileSync(filePath, "utf8");
    return convertYAMLStringToJSON(YAMLContent);
}

/**
 * Writes a JSON object to a YAML file.
 * @param {string} filePath - The path to the YAML file.
 * @param {object} data - The JSON object to write.
 */
export function writeYAMLFile(filePath: string, data: object) {
    const YAMLContent = convertJSONToYAMLString(data);
    fs.writeFileSync(filePath, YAMLContent);
}
