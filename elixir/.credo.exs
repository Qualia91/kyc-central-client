%{
  configs: [
    %{
      name: "default",
      files: %{included: ["lib/", "test/"], excluded: []},
      strict: true,
      checks: %{
        disabled: [
          # KYCCentral.Assessment mirrors the API's assessment response field for
          # field, including the ~20 `*_summary` evidence maps. Splitting it to
          # satisfy a field count would make the struct diverge from the payload
          # it models, which is the opposite of useful here.
          {Credo.Check.Warning.StructFieldAmount, []}
        ]
      }
    }
  ]
}
