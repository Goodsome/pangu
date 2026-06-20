Module -[Defines]-> Class | Function
Class -[Defines]-> Variable | Method
Function | Method -[Defines]-> Parameter
Variable | Parameter -[TypedAs]-> ClassType | UnionTye | GenericType
UionType -[UnionMember] -> ClassType | GenericType
GenericType -[BaseType] -> ClassType
GenericType -[TypeArgument] -> ClassType | UnionType | GenericType
ClassType -[References]-> Class
