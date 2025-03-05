import python_graphql_client
from logging import getLogger
from typing import Optional
from sumatra_client.auth import CognitoJwtAuth
from sumatra_client.config import CONFIG
from sumatra_client.base import BaseClient

logger = getLogger("sumatra.config")


class WorkspaceClient(BaseClient):
    """
    Client to manage workspaces.

    __Humans:__ First, log in via the CLI: `sumatra login`

    __Bots:__ Sorry, no bots allowed

    """

    def __init__(self):
        """
        Create connection object.
        """
        super().__init__(
            client=python_graphql_client.GraphqlClient(
                auth=CognitoJwtAuth("_new"), endpoint=CONFIG.console_graphql_url
            ),
        )

    def get_workspaces(self) -> list[dict[str, str]]:
        """
        Return workspaces, along with metadata, that the current user has access to

        Returns:
            list of dicts containing workspace metadata
        """
        logger.debug("Fetching workspaces")
        query = """
            query CurrentUser($after: String) {
                currentUser {
                    availableRoles(first: 100, after: $after) {
                        nodes {
                            tenant
                            tenantSlug
                            tenantName
                            role
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        """

        variables = {"after": None}
        has_next_page = True
        rows = []
        while has_next_page:
            ret = self._execute_graphql(
                query=query,
                variables=variables,
            )

            for workspace in ret["data"]["currentUser"]["availableRoles"]["nodes"]:
                rows.append(
                    {
                        "slug": workspace["tenantSlug"],
                        "nickname": workspace["tenantName"],
                        "role": workspace["role"],
                        "id": workspace["tenant"],
                    }
                )
            has_next_page = ret["data"]["currentUser"]["availableRoles"]["pageInfo"][
                "hasNextPage"
            ]
            variables["after"] = ret["data"]["currentUser"]["availableRoles"][
                "pageInfo"
            ]["endCursor"]
        return rows

    def create_workspace(
        self,
        workspace: Optional[str] = None,
        nickname: Optional[str] = None,
        app: Optional[str] = None,
    ) -> str:
        """
        Create a new workspace.

        Arguments:
            workspace: Desired slug of the new workspace. Must consist only of letters, numbers, '-', and '_'. If this slug is taken, a random one will be generated instead, which may be changed later.
            nickname: A human readable name for the new workspace. If not provided, the workspace slug will be used.
            app: Name of the application ('optimize' or None)

        Returns:
            slug of newly created workspace
        """

        if workspace is None and nickname is None:
            raise ValueError("Either 'workspace' or 'nickname' must be provided.")

        command = "createTenant"
        if app == "optimize":
            command = "createOptimizeTenant"
        elif app is not None:
            raise ValueError(f"Unknown app '{app}'.")

        query = f"""
            mutation CreateWorkspace($name: String!, $slug: String) {{
                {command}(name: $name, slug: $slug) {{
                    slug
                }}
            }}
        """

        ret = self._execute_graphql(
            query=query,
            variables={"name": nickname or workspace, "slug": workspace},
        )

        return ret["data"][command]["slug"]

    def apply_template(self, workspace: str, template: str) -> None:
        """
        Apply a template to a workspace.

        Arguments:
            workspace: Slug of the workspace to apply the template to.
            template: Name of the template to apply.
        """
        if template != "optimize":
            raise ValueError(f"Unknown template '{template}'.")

        query = """
            mutation ApplyOptimizationTemplate {
                applyOptimizationTemplate 
            }
        """

        self._execute_graphql(
            query=query,
            headers={"x-sumatra-tenant": workspace},
        )

    def delete_workspace(self, workspace: str) -> None:
        """
        Deletes the workspace and all associated data. You must be an owner of the workspace to delete it.

        Warning: This action is not reversible!

        Arguments:
            workspace: Slug of the workspace to delete.
        """

        query = """
            mutation DeleteWorkspace {
                deleteTenant {
                    id
                }
            }
        """

        error_prefix = "Failed to delete workspace"
        try:
            self._execute_graphql(
                query=query,
                headers={"x-sumatra-tenant": workspace},
                error_prefix=error_prefix,
            )
        except RuntimeError as e:
            if str(e).startswith(error_prefix):
                raise ValueError(f"Workspace '{workspace}' not found.")
            else:
                raise e
