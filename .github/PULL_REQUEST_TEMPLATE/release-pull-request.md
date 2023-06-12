<!-- Create a new Release issue before using this template -->

**Description**
<!-- Do not push the release tag until this PR is merged -->
This pull request updates ReQUIAM v0.xx.x -> v0.xx.0. Fixes #<insert associated issue number>

<!-- You may create the pull request after editing the Title and Description above. -->
<!-- The remaining steps can be completed after PR creation -->
  
**Check**
- [ ] Title and description have been updated.
- [ ] Make sure you're on the right branch by checking that [`version.py`](../../../../blob/master/setup.py) contains the updated version number.

**Begin a new release**
:warning: Do not publish the release until this PR is merged :warning:
- [ ] Go to the [New Release](../../../../releases/new) page
- [ ] From the `Choose a tag` dropdown, create a new tag named after the new version. E.g., `v.1.0.1`. The `Target` should be the main or master branch.
- [ ] Click the `Generate release notes` button. Review the notes for accuracy
- [ ] Save the release as Draft.

**Update Documentation**
- [ ] Copy the generated release notes from the previous step to the top of [CHANGELOG.md](../../../../blob/main/CHANGELOG.md)
- [ ] Update [`README.md`](../../../../blob/master/README.md) (if needed)

**Release**
- [ ] Merge this PR
- [ ] Return to [Releases](../../../../releases) and publish the draft release.
