# RESTrict Framework

Please see <https://restrictframework.io> for the most up-to-date documentation.

## TODO

- [X] TODO: Change Ref -> Self visitor to skip data section
- [X] TODO: Write visitor to check Self in data section
- [ ] TODO: Allow stars in security sections
- [X] TODO: Update visitors.MatchRelDeclared...#visit_rel to search mods, too,
      for built-in resources
- [X] TODO: Update visitors.MatchOverridenResource...#visit_resource to
      search mods, too, for built-in resources
- [X] TODO: Consider allowing modification of restrict resources in
      ResolveModifyTypeVisitor

## NOTES

Compiler pipeline steps:

1. [X] Check for duplicate field and resource names
1. [X] Replace refs with func params
1. [X] Replace refs with selfs
1. Resolve declared types
   1. [X] Resolve data constrained field type (res: type)
   1. [X] Resolve rel type (res: bridge, restrict resource, or collection)
   1. [X] Resolve create type (res: bridge or restrict resource)
   1. [X] Resolve base resource type (base: bridge)
1. [X] Resolve inherited fields
1. [X] Resolve inherited rels
1. [X] Resolve inherited effects
1. [X] Resolve inherited security
1. [ ] Resolve inherited workflows
1. [X] Resolve used resources
1. [X] Resolve global names
1. [X] Resolve func referenced function (res: function)
1. Resolve computed types of expressions
   1. [X] Resolve effect field type (res: type or bridge)
   1. [X] Resolve value type (res: type)
   1. [X] Resolve selves type (res: bridge)
   1. [X] Resolve self types (path_res: [bridge, ..., type])
   1. [X] Resolve literal types (res: type)
   1. [X] Resolve tagged literal types (res: type)
   1. [X] Resolve modify type (res: bridge)
   1. [X] Resolve ref type from globals (path_res: type: bridge, ..., type)
1. [X] Check for cycles
1. [X] Resolve data computed field type (func_res: type)
1. [X] Resolve remaining self values
1. Resolve func return type and make sure it matches expected type
   1. [X] Check data constraint (bool)
   1. [X] Check security rule (bool)
   1. [X] Check effect (func_res matches res for referenced field)
1. [X] Compile funcs (compiled)
1. [X] Compile resources

### Expresison types

- Data constraints can include literals, functions, self, selves, tagged
  literals, and value
- Data computed fields can include literals, functions, refs, self, selves,
  and tagged literals
- Effects can include all create, literals, functions, modify, refs, self,
  selves, and tagged literals
- Security can include literals, functions, refs, self, and tagged literals
- Workflows can include literals, refs, self, selves, and tagged literals
