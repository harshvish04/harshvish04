# Setup for github.com/harshvish04

1. Create the special repo (name must equal your username):
       gh repo create harshvish04 --public --clone
   then copy everything from this folder into it.
2. Edit `scripts/config.py` (role, stack, highlights...), then:
       pip install -r scripts/requirements.txt
       python scripts/make_info_card.py
3. (Only if you change your photo)
       python scripts/prep_photo.py source-photo.jpg
       python scripts/make_ascii_svg.py
   Set THEME = "terminal" in make_ascii_svg.py for a dark portrait card.
4. Refresh the heatmap any time:
       python scripts/fetch_contributions.py
       python scripts/render_heatmap_svg.py
5. Push to `main`, then run "Update profile art" once from the Actions tab.

Note: the heatmap shows public contributions only. If your graph is empty,
turn on "Include private contributions on my profile" in GitHub profile settings
(and make some commits) - the scraper reads exactly what your profile shows.
