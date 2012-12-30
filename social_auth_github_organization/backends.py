from urllib2 import HTTPError

from django.conf import settings

from social_auth.utils import dsa_urlopen
from social_auth.backends.contrib.github import GithubBackend, GithubAuth

# GitHub organization configuration
GITHUB_ORGANIZATION_MEMBER_OF_URL = 'https://api.github.com/orgs/{org}/members/{username}'


class GithubOrgBackend(GithubBackend):
    pass


class GithubOrgAuth(GithubAuth):
    AUTH_BACKEND = GithubOrgBackend
    GITHUB_ORGANIZATION = getattr(settings, 'GITHUB_ORGANIZATION', None)

    def user_data(self, access_token, *args, **kwargs):
        data = super(GithubOrgAuth, self).user_data(access_token, *args, **kwargs)
        
        # if we have a github organization defined, test that the current users is
        # a member of that organization.
        if data and self.GITHUB_ORGANIZATION:
            member_url = GITHUB_ORGANIZATION_MEMBER_OF_URL.format(
                org=self.GITHUB_ORGANIZATION,
                username=data.get('login')
            )

            try:
                response = dsa_urlopen(member_url)
            except HTTPError:
                data = None
            else:
                # if the user is a member of the organization, response code will be 204
                # see: http://developer.github.com/v3/orgs/members/#response-if-requester-is-an-organization-member-and-user-is-a-member
                if not response.code == 204:
                    data = None

        return data


BACKENDS = {
    'github': GithubOrgAuth,
}
