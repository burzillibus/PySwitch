import libcst

class AssignmentExtractor:
        
    # Returns a list of all assignments defined on module level, as dicts 
    # {
    #     name: Target name
    #     node: Value node
    # }
    def get(self, cst):
        ret = []

        # Check all statements for function definitions
        for statement in cst.body:
            if not isinstance(statement, libcst.SimpleStatementLine):
                continue

            if not isinstance(statement.body[0], libcst.Assign):
                continue

            assign = statement.body[0]

            for target in assign.targets:
                ret.append({
                    "name": target.target.value,
                    "node": assign.value
                })

        return ret