module.exports = {
    ...require("@redguy12/prettier-config"),
    printWidth: 88,
    bracketSameLine: true,
    bracketSpacing: false,
    jsdocPrintWidth: 101,
    semi: false,
    useTabs: false,
    overrides: [
        ...require("@redguy12/prettier-config").overrides,
        {files: "**.md", options: {proseWrap: "always", printWidth: 101}},
    ],
}
