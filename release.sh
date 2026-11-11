uv version --bump patch            # or minor / major
git commit -am "Release $(uv version --short)"
git tag "v$(uv version --short)"
git push && git push --tags
