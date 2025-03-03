import { expect } from "chai";
import fs from "fs";
import path from "path";

import { readYAMLFile, writeYAMLFile } from "../../src/js/server/yaml";
import { convertJSONToYAMLString, convertYAMLStringToJSON } from "../../src/js/shared/yaml";

describe("YAML operations", () => {
    const testDir = path.join(__dirname, "fixtures");
    const testFilePath = path.join(testDir, "test.yml");

    before(() => {
        if (!fs.existsSync(testDir)) {
            fs.mkdirSync(testDir, { recursive: true });
        }
    });

    after(() => {
        // Cleanup test files
        if (fs.existsSync(testFilePath)) {
            fs.unlinkSync(testFilePath);
        }
        if (fs.existsSync(testDir)) {
            fs.rmdirSync(testDir);
        }
    });

    it("should write and read YAML files", () => {
        const testData = {
            name: "test",
            values: [1, 2, 3],
            nested: {
                key: "value",
            },
        };

        writeYAMLFile(testFilePath, testData);
        const readData = readYAMLFile(testFilePath);
        expect(readData).to.deep.equal(testData);
    });

    it("should handle empty objects", () => {
        const emptyData = {};
        writeYAMLFile(testFilePath, emptyData);
        const readData = readYAMLFile(testFilePath);
        expect(readData).to.deep.equal(emptyData);
    });

    it("should throw error when reading non-existent file", () => {
        const nonExistentPath = path.join(testDir, "nonexistent.yml");
        expect(() => readYAMLFile(nonExistentPath)).to.throw();
    });
});

describe("YAML to JSON conversion", () => {
    const yamlString = `name: test
values:
  - 1
  - 2
  - 3
nested:
  key: value
`;
    const jsonObject = {
        name: "test",
        values: [1, 2, 3],
        nested: {
            key: "value",
        },
    };

    it("should convert YAML string to JSON", () => {
        expect(convertYAMLStringToJSON(yamlString)).to.deep.equal(jsonObject);
    });

    it("should convert JSON to YAML string", () => {
        expect(convertJSONToYAMLString(jsonObject)).to.equal(yamlString);
    });
});
