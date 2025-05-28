Add-Type -AssemblyName PresentationFramework

# Load XAML
[xml]$xaml = Get-Content -Raw -Path '.\window.xaml'
$reader = New-Object System.Xml.XmlNodeReader $xaml
$window = [Windows.Markup.XamlReader]::Load($reader)

# Find UI elements
$categoryList = $window.FindName('CategoryList')
$appList = $window.FindName('AppList')
$searchBox = $window.FindName('SearchBox')

# Load JSON data
$jsonText = Get-Content -Raw -Path '.\apps.json'
$data = ConvertFrom-Json $jsonText

# Define a default icon path (ensure this file exists)
$defaultIcon = Join-Path $PSScriptRoot 'icons\default.ico'

# Fix icon paths to full absolute paths
foreach ($category in $data.categories) {
  # Resolve category icon
  $catIconPath = Resolve-Path -LiteralPath $category.icon -ErrorAction SilentlyContinue
  if ($catIconPath) {
    $category.icon = $catIconPath.ProviderPath
  } elseif (Test-Path $defaultIcon) {
    $category.icon = $defaultIcon
  } else {
    $category.icon = $null
  }
  foreach ($app in $category.apps) {
    $iconPath = Resolve-Path -LiteralPath $app.icon -ErrorAction SilentlyContinue
    if ($iconPath) {
      $app.icon = $iconPath.ProviderPath
    } elseif (Test-Path $defaultIcon) {
      $app.icon = $defaultIcon
    } else {
      $app.icon = $null
    }
  }
}

# Store categories in a variable
$categories = $data.categories

# Bind categories to CategoryList
$categoryList.ItemsSource = $categories

# When category selection changes, update app list
$categoryList.Add_SelectionChanged({
    $selectedCategory = $categoryList.SelectedItem
    if ($null -ne $selectedCategory) {
      $appList.ItemsSource = $selectedCategory.apps
    }
    else {
      $appList.ItemsSource = $null
    }
  })

# Search box filter logic
$searchBox.Add_TextChanged({
    $query = $searchBox.Text.ToLower()

    if ([string]::IsNullOrWhiteSpace($query)) {
      # Show all categories
      $categoryList.ItemsSource = $categories
    }
    else {
      # Filter categories and apps by name
      $filteredCategories = @()
      foreach ($category in $categories) {
        $filteredApps = $category.apps | Where-Object { $_.name.ToLower().Contains($query) }
        if ($category.name.ToLower().Contains($query) -or $filteredApps.Count -gt 0) {
          # Clone the category and replace apps with filteredApps
          $catClone = $category.PSObject.Copy()
          $catClone.apps = @($filteredApps)
          $filteredCategories += $catClone
        }
      }
      $categoryList.ItemsSource = $filteredCategories
    }
  })

# Launch app on double click in AppList
$appList.Add_MouseDoubleClick({
    $selectedApp = $appList.SelectedItem
    if ($null -ne $selectedApp) {
      Start-Process $selectedApp.path
    }
  })

# Find custom title bar and buttons
$closeBtn = $window.FindName('CloseButton')
$minBtn = $window.FindName('MinimizeButton')

# Wire up close and minimize button events
$closeBtn.Add_Click({ $window.Close() })
$minBtn.Add_Click({ $window.WindowState = 'Minimized' })

# Enable dragging the window by the custom title bar (the Border)
$titleBar = $window.Content.Children[0] # The Border is the first child of the root Grid
$titleBar.Add_MouseLeftButtonDown({
    param($s, $e)
    if ($e.ButtonState -eq 'Pressed') {
        $window.DragMove()
    }
})

# Show window
$window.ShowDialog() | Out-Null
