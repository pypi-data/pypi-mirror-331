from typing import Optional
from sumatra_client.client import Client


class OptimizeClient(Client):
    """
    Extension to GraphQL Client to access methods specific
    to Sumatra Optimize.

    __Humans:__ First, log in via the CLI: `sumatra login`

    __Bots:__ Set the `SUMATRA_INSTANCE` and `SUMATRA_SDK_KEY` environment variables
    """

    def __init__(
        self,
        instance: Optional[str] = None,
        branch: Optional[str] = None,
        workspace: Optional[str] = None,
    ):
        """
        Create connection object.

        Arguments:
            instance: Sumatra instance url, e.g. `yourco.sumatra.ai`. If unspecified, the your config default will be used.
            branch: Set default branch. If unspecified, your config default will be used.
            workspace: Sumatra workspace name to connect to.
        """
        super().__init__(
            instance=instance,
            branch=branch,
            workspace=workspace,
        )

    def create_audience(
        self,
        name: str,
        description: Optional[str] = None,
        rule: Optional[dict] = None,
        audience_type: Optional[str] = None,
    ) -> str:
        """
        Create new Audience.

        Arguments:
            name: Human-readable name for the audience.
            description: Optional description of the audience.
            rule: JSON object representing the audience rule.
            audience_type: Either 'SumatraAI' or None

        Returns:
            slug of the created audience
        """

        query = """
            mutation CreateAudience($name: String!, $description: String, $rule: JSON, $audienceType: String) {
                createAudience(name: $name, description: $description, rule: $rule, audienceType: $audienceType) {
                    slug
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={
                "name": name,
                "description": description,
                "rule": rule,
                "audienceType": audience_type,
            },
        )
        return ret["data"]["createAudience"]["slug"]

    def get_audience(self, slug: str) -> dict:
        """
        Get Audience by slug.

        Arguments:
            slug: Audience slug

        Returns:
            Audience details
        """
        query = """
            query GetAudience($slug: String!) {
                audience(slug: $slug) {
                    slug
                    name
                    description
                    rule
                    audienceType
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"slug": slug},
        )
        return ret["data"]["audience"]

    def list_audiences(self) -> list[dict]:
        """
        List all Audiences.

        Returns:
            List of Audiences, including details
        """
        query = """
            query ListAudiences {
                audiences(first: 100) {
                    nodes {
                        slug
                        name
                        description
                        rule
                        audienceType
                    }
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
        )
        return ret["data"]["audiences"]["nodes"]

    def get_audience_inputs(self) -> list[dict]:
        """
        Get list of available audience input features.

        Returns:
            List of scowl feature names and corresponding operators
        """
        query = """
            query GetAudienceInputs {
                audienceInputs {
                    name
                    operators
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
        )
        return ret["data"]["audienceInputs"]

    def delete_audience(self, slug: str) -> None:
        """
        Delete Audience by slug.
        """
        query = """
            mutation DeleteAudience($slug: String!) {
                deleteAudience(slug: $slug) {
                    slug
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={"slug": slug},
        )

    def create_optimization(
        self,
        name: str,
        rootPage: str,
        holdout_percentage: float = 0,
        description: Optional[str] = None,
    ) -> str:
        """
        Create new Optimization.

        Arguments:
            name: Human-readable name for the optimization.
            rootPage: Base URL for the optimization.
            holdout_percentage: Percentage of traffic to hold out for the optimization.
            description: Optional description of the optimization.

        Returns:
            id of the created optimization
        """
        query = """
            mutation CreateOptimization($name: String!, $rootPage: String!, $holdoutPercentage: Float!, $description: String) {
                putOptimization(name: $name, rootPage: $rootPage, holdoutPercentage: $holdoutPercentage, description: $description) {
                    id
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={
                "name": name,
                "rootPage": rootPage,
                "description": description,
                "holdoutPercentage": holdout_percentage,
            },
        )
        return ret["data"]["putOptimization"]["id"]

    def delete_optimization(self, id: str):
        """
        Delete Optimization by id.

        Arguments:
            id: Optimization id
        """
        query = """
            mutation DeleteOptimization($id: String!) {
                deleteOptimization(id: $id) {
                    id
                }
            }
        """
        self._execute_graphql(
            query=query,
            variables={"id": id},
        )

    def get_optimization(self, id: str) -> dict:
        """
        Get Optimization by id.

        Arguments:
            id: Optimization id

        Returns:
            Optimization details
        """
        query = """
            query GetOptimization($id: String!) {
                optimization(id: $id) {
                    id
                    slug
                    name
                    description
                    rootPage
                    holdoutPercentage
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"id": id},
        )
        return ret["data"]["optimization"]

    def list_optimizations(self) -> list[dict]:
        """
        List all Optimizations.

        Returns:
            List of Optimizations, including details
        """
        query = """
                query ListOptimizations {
                    optimizations(first: 10) {
                        nodes {
                            id
                            name
                            slug
                            holdoutPercentage
                            rootPage
                        }
                    }
                }
            """
        ret = self._execute_graphql(
            query=query,
        )
        return ret["data"]["optimizations"]["nodes"]

    def get_goals(self, optimization_id: str) -> list[dict]:
        """
        Get Goals for an Optimization.

        Arguments:
            optimization_id: Optimization id

        Returns:
            List of Goals, including details
        """
        query = """
            query GetGoals($optimizationId: String!) {
                optimization(id: $optimizationId) {
                    goal {
                        type
                        name
                        value
                        path
                    }
                }
            }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"optimizationId": optimization_id},
        )
        return ret["data"]["optimization"]["goal"]

    def create_experience(
        self, optimization_id: str, name: str, audience: str = "everyone"
    ) -> str:
        """
        Create new Experience.

        Arguments:
            optimization_id: Optimization id
            name: Human-readable name for the experience.
            audience: Audience slug

        Returns:
            id of the created experience
        """
        query = """
                mutation CreateExperience($optimizationId: String!, $name: String!, $audience: String!) {
                    createExperience(
                        optimizationId: $optimizationId
                        audiences: [$audience]
                        variants: [{name: "Default", overrides: []}]
                        name: $name
                    ) {
                        ...ExperienceParts
                    }
                }

                fragment ExperienceParts on Experience {
                    id
                    status
                }
        """
        ret = self._execute_graphql(
            query=query,
            variables={
                "optimizationId": optimization_id,
                "name": name,
                "audience": audience,
            },
        )
        return ret["data"]["createExperience"]["id"]

    def list_experiences(self, optimization_id: str) -> list[dict]:
        """
        List all Experiences for an Optimization.

        Arguments:
            optimization_id: Optimization id

        Returns:
            List of Experiences, including details
        """
        query = """
                query ListExperiences($optimizationId: String!) {
                    optimization(id: $optimizationId) {
                        experiences {
                            ...ExperienceParts
                        }
                    }
                }

                fragment ExperienceParts on Experience {
                    id
                    name
                    slug
                    status
                    experimentId
                    audiences {
                        ...AudienceParts
                    }
                    variants {
                        ...VariantParts
                    }
                }

                fragment AudienceParts on Audience {
                    slug
                    name
                }

                fragment VariantParts on Variant {
                    name
                    slug
                    percentage
                    overrides {
                        path
                        selector
                        type
                        value
                        xPath
                    }
                }
        """
        ret = self._execute_graphql(
            query=query,
            variables={"optimizationId": optimization_id},
        )
        return ret["data"]["optimization"]["experiences"]

    def get_experience(self, optimization_id: str, experience_id: str) -> dict:
        """
        Get Experience by id.

        Arguments:
            optimization_id: Optimization id
            experience_id: Experience id

        Returns:
            Experience details
        """
        query = """
                query GetExperience($optimizationId: String!, $experienceId: String!) {
                    optimization(id: $optimizationId) {
                        experience(id: $experienceId) {
                            ...ExperienceParts
                        }
                    }
                }

                fragment ExperienceParts on Experience {
                    id
                    name
                    slug
                    status
                    experimentId
                    audiences {
                        ...AudienceParts
                    }
                    variants {
                        ...VariantParts
                    }
                }

                fragment AudienceParts on Audience {
                    slug
                    name
                }

                fragment VariantParts on Variant {
                    name
                    slug
                    percentage
                    overrides {
                        path
                        selector
                        type
                        value
                        xPath
                    }
                }

                """
        ret = self._execute_graphql(
            query=query,
            variables={
                "optimizationId": optimization_id,
                "experienceId": experience_id,
            },
        )
        return ret["data"]["optimization"]["experience"]

    def update_experience(
        self,
        optimization_id: str,
        experience_id: str,
        status: Optional[str] = None,
        audience: Optional[str] = None,
    ) -> dict:
        """
        Update Experience by id.

        Arguments:
            optimization_id: Optimization id
            experience_id: Experience id
            status: New status for the experience. One of {'draft', 'running', 'stopped'}
            audience: Audience slug

        Returns:
            Experience details
        """
        query = """
                mutation UpdateExperience($optimizationId: String!, $experienceId: String!, $status: String, $audiences: [String]) {
                    updateExperience(
                        optimizationId: $optimizationId
                        experienceId: $experienceId
                        status: $status
                        audiences: $audiences
                    ) {
                        ...ExperienceParts
                    }
                }

                fragment ExperienceParts on Experience {
                    id
                    status
                }
        """
        ret = self._execute_graphql(
            query=query,
            variables={
                "optimizationId": optimization_id,
                "experienceId": experience_id,
                "status": status,
                "audiences": [audience] if audience else None,
            },
        )
        return ret["data"]["updateExperience"]

    def delete_experience(self, optimization_id: str, experience_id: str):
        """
        Delete Experience by id.

        Arguments:
            optimization_id: Optimization id
            experience_id: Experience id
        """
        query = """
                mutation DeleteExperience($optimizationId: String!, $experienceId: String!) {
                    deleteExperience(optimizationId: $optimizationId, experienceId: $experienceId) {
                        id
                    }
                }
        """
        self._execute_graphql(
            query=query,
            variables={
                "optimizationId": optimization_id,
                "experienceId": experience_id,
            },
        )
