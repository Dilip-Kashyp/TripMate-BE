WORKFLOW_DESCRIPTION = """
                Travel Planning Workflow Graph:
                ================================
                [User Query]
                    ↓
                [Extract Intent] → Extract locations, preferences
                    ↓
                [Validate Locations] → Get station codes
                    ↓f
                [Fetch Trains] → Query IRCTC API
                    ↓
                [Analyze Trains] → Filter by preferences
                    ↓
                [Generate Recommendations] → AI analysis
                    ↓
                [Final Response]

                Conditional Edges:
                - If error at any step → END with error
                - If needs clarification → END with clarification request
                - If successful → Continue to next step
            """
ERROR = "error"