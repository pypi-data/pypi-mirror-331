from vtkmodules.vtkCommonCore import vtkUnsignedCharArray, vtkUnsignedIntArray
from vtkmodules.vtkCommonDataModel import vtkPolyData


def set_polydata_colors(data: vtkPolyData, color: tuple) -> vtkUnsignedCharArray:
    n_cells = data.GetNumberOfCells()
    cell_colors = vtkUnsignedCharArray()
    cell_colors.SetName("colors")
    cell_colors.SetNumberOfComponents(3)
    cell_colors.SetNumberOfTuples(n_cells)
    cell_colors.FillComponent(0, color[0])
    cell_colors.FillComponent(1, color[1])
    cell_colors.FillComponent(2, color[2])
    data.GetCellData().SetScalars(cell_colors)
    return cell_colors


def set_polydata_property(data: vtkPolyData, property_data: int, property_name: str) -> vtkUnsignedIntArray:
    n_cells = data.GetNumberOfCells()
    cell_identifier = vtkUnsignedIntArray()
    cell_identifier.SetName(property_name)
    cell_identifier.SetNumberOfTuples(n_cells)
    cell_identifier.Fill(property_data)
    data.GetCellData().AddArray(cell_identifier)
    return cell_identifier