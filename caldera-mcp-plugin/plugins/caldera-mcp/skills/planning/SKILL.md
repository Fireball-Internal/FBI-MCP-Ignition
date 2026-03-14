---
name: planning
description: >
  Plan new Ignition Perspective features by analyzing existing gateway patterns,
  component schemas, and design guidance. Use when the user has a feature request,
  user story, or wants to build something new - a new screen, dashboard, equipment
  detail view, alarm display, or navigation structure. Covers exploring existing
  conventions, checking component availability via search_components and
  get_component_schema, ISA-101/HMI design guidance, verifying data sources, and
  proposing view hierarchies grounded in what actually exists on the gateway.
---

# Planning Ignition Perspective Features

Help experienced Ignition developers plan new features by analyzing what already exists on the
gateway and proposing designs grounded in real data. Every recommendation should cite what you
actually observed, not generic advice.

**Be direct. Lead with findings, not preamble.**

## First Interaction

On your first interaction with this gateway, silently call `caldera:get_gateway_health` to orient
yourself. Note the gateway version, bridge status, and project list for your own context. Do NOT
dump this to the user unless they ask or something is wrong. Check if this is a QA or production
server - if production, stop and warn the user immediately.

## Feature Planning Workflow

1. **Explore what exists** - understand the project's structure, naming conventions, and
   patterns already in use:
   ```
   caldera:get_project_overview(project)
   caldera:list_views(project)
   caldera:list_scripts(project)
   ```

2. **Find similar implementations** - search for existing views that solve related problems.
   Read a few representative views to understand the team's conventions:
   ```
   caldera:search_views(project, query)
   caldera:read_view(project, similar_view_path)
   ```

3. **Check available components** - identify the right components and understand their schemas:
   ```
   caldera:search_components(query, category)
   caldera:get_component_schema(component_type)
   caldera:get_design_guidance(topic)
   ```

4. **Verify data availability** - confirm the data sources the feature needs actually exist
   and return the expected shape:
   ```
   caldera:browse_tags("[default]relevant/path")
   caldera:read_tags(tag_paths)
   caldera:list_named_queries(project)
   caldera:execute_script(probe_code)
   ```

5. **Propose a plan** - suggest view hierarchy, component choices, data binding strategy, and
   any new tags/queries/scripts needed. Ground every recommendation in observed gateway state.

## Schema and Design Reference

Your reference library for well-informed recommendations:

- `caldera:search_components(query, category)` - find component types by keyword or category
- `caldera:get_component_schema(type)` - full property schema with events and examples
- `caldera:get_binding_schema(type)` - tag, property, expression, or query binding reference
- `caldera:get_expression_reference(function_name, category)` - expression language docs
- `caldera:get_design_guidance(topic)` - ISA-101/EEMUA 201 HMI design guidance (14 topics)
- `caldera:search_icons(query, library)` - icon search across all Perspective libraries

## Design Guidance Topics

`caldera:get_design_guidance` covers: color, layout, navigation, alarms, trends, typography,
animation, data-entry, hierarchy, symbols, responsive, accessibility, performance, security.

## Avoiding Common Pitfalls in New Designs

When proposing new views, be aware of Perspective's silent failure modes that frequently catch
developers. These are especially important to avoid in new designs.

For the full catalog, see [perspective-pitfalls.md](../../reference/perspective-pitfalls.md).

## Grounding Recommendations

Every recommendation should cite observed gateway state:
- "I see you're using flex repeaters with embedded views for equipment screens in /Equipment/* - I'd suggest the same pattern here."
- "Your existing alarm views use tag bindings with [default]Alarms/ paths - the data source for this feature should follow the same convention."
