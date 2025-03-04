from dependency_injector import containers, providers


class RepositoryContainer(containers.DeclarativeContainer):
    pass


class UseCaseContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()


class ControllerContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()
    use_cases = providers.DependenciesContainer()


class ApplicationContainer(containers.DeclarativeContainer):
    repositories = providers.Container(RepositoryContainer)
    use_cases = providers.Container(UseCaseContainer, repositories=repositories)
    controllers = providers.Container(
        ControllerContainer, repositories=repositories, use_cases=use_cases
    )
